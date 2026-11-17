from pathlib import Path
import gradio as gr
import requests
API_URL = "http://127.0.0.1:8000"

def upload_pdfs(files):
    if not files:
        return "Please choose one or more PDFs first."
    if not isinstance(files, list):
        files = [files]
    
    logs = []
    for file_path in files:
        filename = Path(file_path).name
        try:
            with open(file_path, "rb") as f:
                r = requests.post(f"{API_URL}/upload", files={"file": (filename, f, "application/pdf")}, timeout=600)
            if r.ok:
                data = r.json()
                logs.append(
                    f"✅ **{filename}**: Indexed {data.get('text_chunks', 0)} text chunks, "
                    f"{data.get('tables', 0)} tables (Cohere), {data.get('figures', 0)} diagrams (Nova Multimodal)"
                )
            else:
                logs.append(f"❌ **{filename}**: Upload failed ({r.status_code}) - {r.text[:200]}")
        except Exception as e:
            logs.append(f"❌ **{filename}**: Error - {e}")
    return "\n\n".join(logs)

def ask(question):
    if not question.strip():
        return "Enter a question.", ""
    r = requests.post(f"{API_URL}/ask", json={"question": question}, timeout=600)
    if not r.ok:
        return f"Request failed: {r.status_code} {r.text}", ""
    data = r.json()
    return data.get("answer", ""), data.get("review", "")

with gr.Blocks(title="ResearchIQ — Multimodal Research Assistant") as demo:
    gr.Markdown("# ResearchIQ\nUpload research papers, ask questions, compare findings and inspect evidence.")
    with gr.Tab("Upload papers"):
        pdf_files = gr.File(
            label="Research papers (Select one or multiple PDFs)",
            file_types=[".pdf"],
            file_count="multiple",
            type="filepath"
        )
        upload_btn = gr.Button("Upload and index all selected papers", variant="primary")
        upload_status = gr.Markdown()
        upload_btn.click(upload_pdfs, inputs=pdf_files, outputs=upload_status)
    with gr.Tab("Ask ResearchIQ"):
        question = gr.Textbox(label="Question", lines=3, placeholder="Compare the methods and results across the uploaded papers...")
        ask_btn = gr.Button("Ask", variant="primary")
        answer = gr.Markdown()
        review = gr.Textbox(label="AutoGen review notes", lines=8)
        ask_btn.click(ask, inputs=question, outputs=[answer, review])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
