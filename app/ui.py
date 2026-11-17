import uuid
from pathlib import Path
import gradio as gr
import requests
from app.storage import save_upload, ensure_dirs
from app.ingestion import ingest_pdf
from app.graph import ask_researchiq
import asyncio

API_URL = "http://127.0.0.1:8000"

def upload_pdfs(files, progress=gr.Progress(track_tqdm=True)):
    if not files:
        yield "⚠️ **Please select or drop one or more PDF files above before clicking Upload.**"
        return
    if not isinstance(files, list):
        files = [files]
    
    ensure_dirs()
    total = len(files)
    logs = [f"🚀 **Received {total} paper(s). Starting extraction and multi-index ingestion...**\n"]
    yield "\n\n".join(logs)
    
    for idx, file_item in enumerate(files, start=1):
        if isinstance(file_item, str):
            f_path = file_item
        elif hasattr(file_item, "name") and file_item.name:
            f_path = file_item.name
        elif hasattr(file_item, "path") and file_item.path:
            f_path = file_item.path
        elif isinstance(file_item, dict) and "path" in file_item:
            f_path = file_item["path"]
        else:
            f_path = str(file_item)
            
        filename = Path(f_path).name
        progress((idx - 1) / total, desc=f"Processing [{idx}/{total}]: {filename}")
        logs.append(f"⏳ **[{idx}/{total}] Ingesting `{filename}`...** (extracting text, Cohere tables, and Nova Multimodal diagrams)")
        yield "\n\n".join(logs)
        
        try:
            data = Path(f_path).read_bytes()
            paper_id = uuid.uuid4().hex[:10]
            saved_path = save_upload(data, filename, paper_id)
            res = ingest_pdf(saved_path, filename)
            
            logs[-1] = (
                f"✅ **[{idx}/{total}] `{filename}`:** Indexed {res.get('text_chunks', 0)} text chunks, "
                f"{res.get('tables', 0)} tables (Cohere Embed v3), {res.get('figures', 0)} diagrams (Nova Multimodal)"
            )
        except Exception as e:
            logs[-1] = f"❌ **[{idx}/{total}] `{filename}`:** Error during ingestion: {e}"
        
        progress(idx / total, desc=f"Completed {filename}")
        yield "\n\n".join(logs)
        
    logs.append("\n🎉 **All selected papers have been successfully indexed! Switch to the 'Ask ResearchIQ' tab to query them.**")
    yield "\n\n".join(logs)

async def ask_async(question):
    if not question.strip():
        return "⚠️ Please enter a question.", ""
    try:
        res = await ask_researchiq(question)
        answer = res.get("answer", "")
        review = res.get("autogen_review", "")
        return answer, review
    except Exception as e:
        return f"Error executing query: {e}", ""

def ask(question):
    return asyncio.run(ask_async(question))

with gr.Blocks(title="ResearchIQ — Multimodal Research Assistant") as demo:
    gr.Markdown("# ResearchIQ — Multimodal AI Research Assistant\nUpload research papers, ask questions, compare findings, inspect visual diagrams, and verify evidence.")
    
    with gr.Tab("Upload papers"):
        gr.Markdown("### 📄 Select one or multiple research papers (PDF)")
        pdf_files = gr.File(
            label="Drop PDFs here or click to browse",
            file_types=[".pdf"],
            file_count="multiple",
            type="filepath"
        )
        upload_btn = gr.Button("Upload and index all selected papers", variant="primary", size="lg")
        upload_status = gr.Markdown(value="*Status will appear here when you click Upload.*")
        upload_btn.click(upload_pdfs, inputs=pdf_files, outputs=upload_status)
        
    with gr.Tab("Ask ResearchIQ"):
        gr.Markdown("### 💬 Ask cross-paper research, visual, or comparative questions")
        question = gr.Textbox(
            label="Your Research Question",
            lines=3,
            placeholder="e.g. Compare the architectures proposed in CRAG and Self-RAG. How do they handle low-quality retrieval?"
        )
        ask_btn = gr.Button("Ask ResearchIQ", variant="primary", size="lg")
        answer = gr.Markdown(label="Evidence-Grounded Answer")
        review = gr.Textbox(label="Peer Review & Validation Team Notes", lines=7)
        ask_btn.click(ask, inputs=question, outputs=[answer, review])

if __name__ == "__main__":
    demo.queue(default_concurrency_limit=5).launch(server_name="0.0.0.0", server_port=7860)
