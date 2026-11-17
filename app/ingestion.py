import hashlib, re
from pathlib import Path
import fitz
import pdfplumber
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from app.clients import get_embeddings, get_table_embeddings, get_bedrock_runtime
from app.config import settings
from app.storage import upload_visual, ensure_dirs

def _paper_id(path: str) -> str:
    return hashlib.sha1(Path(path).read_bytes()).hexdigest()[:12]

def _make_doc(text, metadata):
    clean = re.sub(r"\s+", " ", text).strip()
    return Document(page_content=clean, metadata=metadata) if clean else None

def describe_figure_with_nova(image_path: str, page_no: int, paper_name: str) -> str:
    """Use Amazon Nova Multimodal to generate a rich visual and diagram embedding description."""
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
            modelId=settings.bedrock_chat_model,
            messages=[{"role": "user", "content": [
                {"text": prompt},
                {"image": {"format": "png", "source": {"bytes": image_bytes}}}
            ]}],
            inferenceConfig={"temperature": 0, "maxTokens": 450}
        )
        return resp["output"]["message"]["content"][0].get("text", "")
    except Exception as exc:
        return f"Visual diagram on page {page_no} of {paper_name}."

def ingest_pdf(path: str, original_name: str) -> dict:
    ensure_dirs()
    paper_id = _paper_id(path)
    text_docs, table_docs, figure_docs = [], [], []
    pdf = fitz.open(path)
    for page_idx, page in enumerate(pdf):
        page_no = page_idx + 1
        doc = _make_doc(page.get_text("text"), {
            "paper_id": paper_id, "paper_name": original_name,
            "page": page_no, "kind": "text", "source": original_name
        })
        if doc:
            text_docs.append(doc)

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
                image_path = str(Path(settings.upload_dir) / f"{paper_id}_{visual_id}.png")
                pix.save(image_path)
                uri = upload_visual(image_path, paper_id, visual_id)

                # Generate rich visual embedding content using Amazon Nova Multimodal
                nova_visual_summary = describe_figure_with_nova(image_path, page_no, original_name)
                
                figure_docs.append(Document(
                    page_content=(
                        f"Figure/Diagram on page {page_no} of {original_name} (Visual ID: {visual_id}):\n"
                        f"{nova_visual_summary}"
                    ),
                    metadata={"paper_id": paper_id, "paper_name": original_name,
                              "page": page_no, "kind": "figure", "visual_id": visual_id,
                              "image_uri": uri, "source": original_name}
                ))
            except Exception:
                continue

    # Table extraction as page-scoped text with Cohere table embeddings
    with pdfplumber.open(path) as pdfp:
        for page_idx, page in enumerate(pdfp.pages):
            try:
                for table_idx, table in enumerate(page.extract_tables() or [], start=1):
                    rows = [" | ".join(str(c or "") for c in row) for row in table]
                    content = "\n".join(rows).strip()
                    if content:
                        table_docs.append(Document(
                            page_content=f"Extracted Table {table_idx} (Page {page_idx+1}, {original_name}):\n{content}",
                            metadata={"paper_id": paper_id, "paper_name": original_name,
                                      "page": page_idx+1, "kind": "table",
                                      "table_id": f"p{page_idx+1}_table{table_idx}",
                                      "source": original_name}
                        ))
            except Exception:
                pass

    splitter = RecursiveCharacterTextSplitter(chunk_size=1100, chunk_overlap=160)
    text_docs = splitter.split_documents(text_docs)
    for i, d in enumerate(text_docs):
        d.metadata["chunk_id"] = f"{paper_id}_text_{i}"
    for i, d in enumerate(table_docs):
        d.metadata["chunk_id"] = f"{paper_id}_table_{i}"
    for i, d in enumerate(figure_docs):
        d.metadata["chunk_id"] = f"{paper_id}_figure_{i}"

    # 1. Text Index (Amazon Titan Text v2)
    if text_docs:
        Chroma(
            collection_name="researchiq_text",
            persist_directory=settings.chroma_dir,
            embedding_function=get_embeddings(),
        ).add_documents(text_docs)

    # 2. Table and Chart Index (Cohere Embed English v3)
    if table_docs:
        Chroma(
            collection_name="researchiq_tables",
            persist_directory=settings.chroma_dir,
            embedding_function=get_table_embeddings(),
        ).add_documents(table_docs)

    # 3. Visuals and Diagrams Index (Nova Multimodal representation)
    if figure_docs:
        Chroma(
            collection_name="researchiq_figures",
            persist_directory=settings.chroma_dir,
            embedding_function=get_embeddings(),
        ).add_documents(figure_docs)

    return {"paper_id": paper_id, "paper_name": original_name,
            "text_chunks": len(text_docs), "tables": len(table_docs),
            "figures": len(figure_docs)}
