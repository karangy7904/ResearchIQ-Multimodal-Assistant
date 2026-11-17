import uuid, time, asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import gradio as gr
from app.storage import save_upload, ensure_dirs
from app.ingestion import ingest_pdf
from app.graph import ask_researchiq, ask_researchiq_stream

def _process_single_paper(file_item):
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
    try:
        t0 = time.time()
        data = Path(f_path).read_bytes()
        paper_id = uuid.uuid4().hex[:10]
        saved_path = save_upload(data, filename, paper_id)
        res = ingest_pdf(saved_path, filename)
        duration = round(time.time() - t0, 1)
        return True, filename, res, duration, None
    except Exception as e:
        return False, filename, None, 0, str(e)

def upload_pdfs(files, progress=gr.Progress(track_tqdm=True)):
    if not files:
        yield "⚠️ **Please select or drop one or more PDF files above before clicking Upload.**"
        return
    if not isinstance(files, list):
        files = [files]

    ensure_dirs()
    total = len(files)
    concurrency = min(total, 8)
    t_start = time.time()
    
    logs = [
        f"🚀 **Received {total} paper(s). Starting parallel ingestion across {concurrency} concurrent workers...**",
        "⚡ Extracting text (Titan v2), tabular metrics (Cohere Embed v3), and diagrams (Nova Multimodal) simultaneously in parallel threads...\n"
    ]
    yield "\n\n".join(logs)

    completed = 0
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        future_map = {executor.submit(_process_single_paper, f): f for f in files}
        for future in as_completed(future_map):
            completed += 1
            success, filename, res, dur, err = future.result()
            if success:
                logs.append(
                    f"✅ **[{completed}/{total}] `{filename}`** ({dur}s): Indexed {res.get('text_chunks', 0)} text chunks, "
                    f"{res.get('tables', 0)} tables (Cohere Embed v3), {res.get('figures', 0)} diagrams (Nova Multimodal)"
                )
            else:
                logs.append(f"❌ **[{completed}/{total}] `{filename}`:** Ingestion error: {err}")
            progress(completed / total, desc=f"Parallel Ingestion: {completed}/{total} finished")
            yield "\n\n".join(logs)

    total_time = round(time.time() - t_start, 1)
    logs.append(f"\n🎉 **All {total} papers successfully processed in parallel in {total_time}s! Switch to 'Ask ResearchIQ' tab to query them.**")
    yield "\n\n".join(logs)

def ask_handler(question, mode):
    if not question.strip():
        yield "⚠️ Please enter a question.", ""
        return

    if "Fast" in mode:
        for partial_answer, notes in ask_researchiq_stream(question):
            yield partial_answer, notes
    else:
        yield "🔬 *Running deep multi-agent deliberation (CrewAI Team + AutoGen Reviewer)...*", "Deliberating across agent personas..."
        res = asyncio.run(ask_researchiq(question))
        yield res.get("answer", ""), res.get("autogen_review", "")

with gr.Blocks(title="ResearchIQ — Multimodal Research Assistant") as demo:
    gr.Markdown("# ResearchIQ — Multimodal AI Research Assistant\nUpload research papers, ask questions, compare findings, inspect visual diagrams, and verify evidence.")

    with gr.Tab("Upload papers"):
        gr.Markdown("### 📄 Select or drop multiple research papers (e.g. 4+ PDFs at once)")
        pdf_files = gr.File(
            label="Drop multiple PDFs here or click to browse",
            file_types=[".pdf"],
            file_count="multiple",
            type="filepath"
        )
        upload_btn = gr.Button("⚡ Upload and Index All Selected Papers (Parallel)", variant="primary", size="lg")
        upload_status = gr.Markdown(value="*Status will appear here when you click Upload.*")
        upload_btn.click(upload_pdfs, inputs=pdf_files, outputs=upload_status)

    with gr.Tab("Ask ResearchIQ"):
        gr.Markdown("### 💬 Ask cross-paper research, visual, or comparative questions")
        question = gr.Textbox(
            label="Your Research Question",
            lines=3,
            placeholder="e.g. Compare the architectures proposed in CRAG and Self-RAG. How do they handle low-quality retrieval?"
        )
        mode = gr.Radio(
            choices=["⚡ Fast Streaming (sub-3s TTFT)", "🔬 Deep Multi-Agent Consensus"],
            value="⚡ Fast Streaming (sub-3s TTFT)",
            label="Answering Mode"
        )
        ask_btn = gr.Button("Ask ResearchIQ", variant="primary", size="lg")
        answer = gr.Markdown(label="Evidence-Grounded Answer")
        review = gr.Textbox(label="Retrieved Sources & Validation Notes", lines=7)
        ask_btn.click(ask_handler, inputs=[question, mode], outputs=[answer, review])

if __name__ == "__main__":
    demo.queue(default_concurrency_limit=8).launch(server_name="0.0.0.0", server_port=7860)
