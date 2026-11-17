from pathlib import Path
import gradio as gr
import requests
API_URL = "http://127.0.0.1:8000"

def upload_pdf(file):
    if file is None:
        return "Choose a PDF first."
    filename = Path(file).name
    with open(file, "rb") as f:
        r = requests.post(f"{API_URL}/upload", files={"file": (filename, f, "application/pdf")}, timeout=600)
    return r.text if r.ok else f"Upload failed: {r.status_code} {r.text}"

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
        pdf = gr.File(label="Research paper (PDF)", file_types=[".pdf"], type="filepath")
        upload_btn = gr.Button("Upload and index")
        upload_status = gr.Textbox(label="Ingestion result", lines=5)
        upload_btn.click(upload_pdf, inputs=pdf, outputs=upload_status)
    with gr.Tab("Ask ResearchIQ"):
        question = gr.Textbox(label="Question", lines=3, placeholder="Compare the methods and results across the uploaded papers...")
        ask_btn = gr.Button("Ask")
        answer = gr.Markdown()
        review = gr.Textbox(label="AutoGen review notes", lines=8)
        ask_btn.click(ask, inputs=question, outputs=[answer, review])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
