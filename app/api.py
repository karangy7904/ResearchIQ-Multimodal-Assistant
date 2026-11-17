import uuid
from typing import Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from app.config import settings
from app.storage import ensure_dirs, save_upload, purge_session
from app.ingestion import ingest_pdf
from app.graph import ask_researchiq

app = FastAPI(title="ResearchIQ API", version="1.0.0")

class AskRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

@app.on_event("startup")
def startup():
    ensure_dirs()

@app.get("/health")
def health():
    return {"status": "ok", "service": "ResearchIQ"}

@app.post("/upload")
async def upload_paper(file: UploadFile = File(...), session_id: Optional[str] = Form(None)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")
    data = await file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB.")
    paper_id = uuid.uuid4().hex[:10]
    path = save_upload(data, file.filename, paper_id, session_id=session_id)
    result = ingest_pdf(path, file.filename, session_id=session_id)
    return {"status": "indexed", "session_id": session_id, **result}

def _ingest_bytes_file(file_info):
    data, filename, session_id = file_info
    paper_id = uuid.uuid4().hex[:10]
    path = save_upload(data, filename, paper_id, session_id=session_id)
    return ingest_pdf(path, filename, session_id=session_id)

@app.post("/upload-batch")
async def upload_papers_batch(files: list[UploadFile] = File(...), session_id: Optional[str] = Form(None)):
    valid_files = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue
        data = await file.read()
        if len(data) > settings.max_upload_mb * 1024 * 1024:
            continue
        valid_files.append((data, file.filename, session_id))

    results = []
    if valid_files:
        with ThreadPoolExecutor(max_workers=min(len(valid_files), 8)) as executor:
            futures = [executor.submit(_ingest_bytes_file, item) for item in valid_files]
            for fut in as_completed(futures):
                try:
                    results.append(fut.result())
                except Exception as e:
                    results.append({"error": str(e)})

    return {"status": "indexed_batch", "session_id": session_id, "papers_count": len(results), "papers": results}

@app.delete("/session/{session_id}")
def end_session(session_id: str):
    """Purge all ephemeral data, vectors, tables, diagrams, and files for a private session."""
    purge_session(session_id)
    return {
        "status": "purged",
        "session_id": session_id,
        "message": "All session data, vectors, tables, and files permanently removed."
    }

@app.post("/ask")
async def ask(req: AskRequest):
    result = await ask_researchiq(req.question, session_id=req.session_id)
    return {"answer": result.get("answer", ""), "citations": result.get("citations", []),
            "intent": result.get("intent"), "review": result.get("autogen_review", ""),
            "evidence_check": result.get("evidence_check", "")}
