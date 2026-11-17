import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.config import settings
from app.storage import ensure_dirs, save_upload
from app.ingestion import ingest_pdf
from app.graph import ask_researchiq

app = FastAPI(title="ResearchIQ API", version="1.0.0")

class AskRequest(BaseModel):
    question: str

@app.on_event("startup")
def startup():
    ensure_dirs()

@app.get("/health")
def health():
    return {"status": "ok", "service": "ResearchIQ"}

@app.post("/upload")
async def upload_paper(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")
    data = await file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB.")
    paper_id = uuid.uuid4().hex[:10]
    path = save_upload(data, file.filename, paper_id)
    result = ingest_pdf(path, file.filename)
    return {"status": "indexed", **result}

@app.post("/upload-batch")
async def upload_papers_batch(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue
        data = await file.read()
        if len(data) > settings.max_upload_mb * 1024 * 1024:
            continue
        paper_id = uuid.uuid4().hex[:10]
        path = save_upload(data, file.filename, paper_id)
        result = ingest_pdf(path, file.filename)
        results.append(result)
    return {"status": "indexed_batch", "papers_count": len(results), "papers": results}

@app.post("/ask")
async def ask(req: AskRequest):
    result = await ask_researchiq(req.question)
    return {"answer": result.get("answer", ""), "citations": result.get("citations", []),
            "intent": result.get("intent"), "review": result.get("autogen_review", ""),
            "evidence_check": result.get("evidence_check", "")}
