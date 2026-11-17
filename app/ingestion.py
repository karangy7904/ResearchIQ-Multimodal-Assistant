import hashlib, re, threading 
from pathlib import Path
import fitz
import pdfplumber
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from app.clients import get_embeddings, get_table_embeddings, get_bedrock_runtime
from app.config import settings
from app.storage import upload_visual, ensure_dirs

_CHROMA_LOCK = threading.Lock()

def _paper_id(path: str) -> str:
    return hashlib.sha1(Path(path).read_bytes()).hexdigest()[:12]

def _make_doc(text, metadata):
    clean = re.sub(r"\s+", " ", text).strip()
    return Document(page_content=clean, metadata=metadata) if clean else None

def describe_figure_with_nova(image_path: str, page_no: int, paper_name: str) -> str:
    """Use Amazon Nova Multimodal (Nova Lite) for rapid, high-accuracy visual embedding summaries."""
    try:
        runtime = get_bedrock_runtime()
        image_bytes = Path(image_path).read_bytes()
        prompt = (
            f"You are a multimodal research analyst. Analyze this figure/diagram from {paper_name}, page {page_no}.\n"
            "Provide a dense, structured technical summary for vector search retrieval:\n"
            "1. Type: (Architecture Diagram, Workflow, Flowchart, Experimental Result Plot, or Ablation Chart)\n"
            "2. Visual Components: Key modules, entities, pathways, arrows, and block names\n"
            "3. Metrics & Data: Axes labels, legends, units, comparisons, and highlighted data points if legible\n"
            "4. Core Supported Takeaway: What technical hypothesis, mechanism, or empirical finding does this visual prove?\n"
            "Be factual and technical. Do not guess unreadable values."
        )
        resp = runtime.converse(
            modelId="apac.amazon.nova-lite-v1:0",
            messages=[{"role": "user", "content": [
                {"text": prompt},
                {"image": {"format": "png", "source": {"bytes": image_bytes}}}
            ]}],
            inferenceConfig={"temperature": 0, "maxTokens": 250}
        )
        return resp["output"]["message"]["content"][0].get("text", "")
    except Exception as exc:
        return f"Visual diagram on page {page_no} of {paper_name}."

def ingest_pdf(path: str, original_name: str, session_id: str = None) -> dict:
    ensure_dirs()
    paper_id = _paper_id(path)
    text_docs, table_docs, figure_docs = [], [], []
    pdf = fitz.open(path)
    for page_idx, page in enumerate(pdf):
        page_no = page_idx + 1
        meta = {
            "paper_id": paper_id, "paper_name": original_name,
            "page": page_no, "kind": "text", "source": original_name
        }
        if session_id:
            meta["session_id"] = session_id

        doc = _make_doc(page.get_text("text"), meta)
        if doc:
            text_docs.append(doc)

        # Fast C++ table extraction via PyMuPDF
        try:
            tabs = page.find_tables()
            for table_idx, tab in enumerate(tabs, start=1):
                raw_rows = tab.extract()
                if not raw_rows:
                    continue
                rows = [" | ".join(str(c or "") for c in row) for row in raw_rows]
                content = "\n".join(rows).strip()
                if not content:
                    continue

                table_meta = {
                    "paper_id": paper_id, "paper_name": original_name,
                    "page": page_no, "kind": "table",
                    "table_id": f"p{page_no}_table{table_idx}",
                    "source": original_name
                }
                if session_id:
                    table_meta["session_id"] = session_id

                # Cohere Embed v3 enforces a strict 2048 character limit per document.
                if len(content) > 1800:
                    header = rows[0] if rows else ""
                    current_chunk = [f"Extracted Table {table_idx} (Page {page_no}, {original_name}) [Header: {header}]:"]
                    current_len = len(current_chunk[0])
                    for row in rows:
                        if current_len + len(row) + 1 > 1800:
                            table_docs.append(Document(
                                page_content="\n".join(current_chunk)[:1900],
                                metadata=dict(table_meta)
                            ))
                            current_chunk = [f"Extracted Table {table_idx} cont. (Page {page_no}, {original_name}) [Header: {header}]:", row]
                            current_len = sum(len(x) for x in current_chunk) + len(current_chunk)
                        else:
                            current_chunk.append(row)
                            current_len += len(row) + 1
                    if len(current_chunk) > 1:
                        table_docs.append(Document(
                            page_content="\n".join(current_chunk)[:1900],
                            metadata=dict(table_meta)
                        ))
                else:
                    table_docs.append(Document(
                        page_content=f"Extracted Table {table_idx} (Page {page_no}, {original_name}):\n{content}",
                        metadata=dict(table_meta)
                    ))
        except Exception:
            pass

        # Extract embedded figures/images; retain page-level provenance.
        for img_idx, img in enumerate(page.get_images(full=True), start=1):
            xref = img[0]
            try:
                pix = fitz.Pixmap(pdf, xref)
                if pix.n - pix.alpha > 3:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                
                # Filter out tiny icon glyphs/bullets
                if pix.width < 100 or pix.height < 100:
                    continue

                visual_id = f"p{page_no}_img{img_idx}"
                dest_dir = Path(settings.upload_dir) / session_id if session_id else Path(settings.upload_dir)
                dest_dir.mkdir(parents=True, exist_ok=True)
                image_path = str(dest_dir / f"{paper_id}_{visual_id}.png")
                pix.save(image_path)
                uri = upload_visual(image_path, paper_id, visual_id)

                # High-speed local indexing: store visual provenance without blocking on cloud vision
                visual_summary = (
                    f"Figure/Diagram on page {page_no} of {original_name} (Visual ID: {visual_id}). "
                    f"Multimodal architecture/data diagram available locally for visual inspection."
                )
                
                fig_meta = {
                    "paper_id": paper_id, "paper_name": original_name,
                    "page": page_no, "kind": "figure", "visual_id": visual_id,
                    "image_uri": uri, "source": original_name
                }
                if session_id:
                    fig_meta["session_id"] = session_id

                figure_docs.append(Document(
                    page_content=visual_summary,
                    metadata=fig_meta
                ))
            except Exception:
                continue

    # Optimized chunk size (2000 chars) cuts Bedrock embedding calls in half while retaining rich context
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    text_docs = splitter.split_documents(text_docs)
    for i, d in enumerate(text_docs):
        d.metadata["chunk_id"] = f"{paper_id}_text_{i}"
    for i, d in enumerate(table_docs):
        d.metadata["chunk_id"] = f"{paper_id}_table_{i}"
    for i, d in enumerate(figure_docs):
        d.metadata["chunk_id"] = f"{paper_id}_figure_{i}"

    # Precompute embeddings concurrently OUTSIDE the lock across all threads
    # 1. Text Index (Amazon Titan Text v2)
    if text_docs:
        text_texts = [d.page_content for d in text_docs]
        text_metas = [d.metadata for d in text_docs]
        text_ids = [d.metadata["chunk_id"] for d in text_docs]
        text_embeds = get_embeddings().embed_documents(text_texts)
    else:
        text_embeds, text_texts, text_metas, text_ids = [], [], [], []

    # 2. Table Index (Cohere Embed English v3 - max 2048 chars)
    if table_docs:
        for td in table_docs:
            if len(td.page_content) > 1900:
                td.page_content = td.page_content[:1900]
        table_texts = [d.page_content for d in table_docs]
        table_metas = [d.metadata for d in table_docs]
        table_ids = [d.metadata["chunk_id"] for d in table_docs]
        table_embeds = get_table_embeddings().embed_documents(table_texts)
    else:
        table_embeds, table_texts, table_metas, table_ids = [], [], [], []

    # 3. Figure Index (Titan Text v2 representation)
    if figure_docs:
        fig_texts = [d.page_content for d in figure_docs]
        fig_metas = [d.metadata for d in figure_docs]
        fig_ids = [d.metadata["chunk_id"] for d in figure_docs]
        fig_embeds = get_embeddings().embed_documents(fig_texts)
    else:
        fig_embeds, fig_texts, fig_metas, fig_ids = [], [], [], []

    col_text = f"text_{session_id}" if session_id else "researchiq_text"
    col_tables = f"tables_{session_id}" if session_id else "researchiq_tables"
    col_figures = f"figures_{session_id}" if session_id else "researchiq_figures"

    # Fast thread-safe local SQLite writes (only held for <50ms per paper)
    with _CHROMA_LOCK:
        if text_embeds:
            Chroma(collection_name=col_text, persist_directory=settings.chroma_dir)._collection.upsert(
                ids=text_ids, embeddings=text_embeds, metadatas=text_metas, documents=text_texts
            )
        if table_embeds:
            Chroma(collection_name=col_tables, persist_directory=settings.chroma_dir)._collection.upsert(
                ids=table_ids, embeddings=table_embeds, metadatas=table_metas, documents=table_texts
            )
        if fig_embeds:
            Chroma(collection_name=col_figures, persist_directory=settings.chroma_dir)._collection.upsert(
                ids=fig_ids, embeddings=fig_embeds, metadatas=fig_metas, documents=fig_texts
            )

    return {"paper_id": paper_id, "paper_name": original_name, "session_id": session_id,
            "text_chunks": len(text_docs), "tables": len(table_docs),
            "figures": len(figure_docs)}
