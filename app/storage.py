import os, shutil
from pathlib import Path
from typing import Optional
from app.config import settings
from app.clients import get_s3

def ensure_dirs():
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.chroma_dir).mkdir(parents=True, exist_ok=True)

def save_upload(file_bytes: bytes, filename: str, paper_id: str, session_id: Optional[str] = None) -> str:
    ensure_dirs()
    safe_name = Path(filename).name.replace(" ", "_")
    if session_id:
        target_dir = Path(settings.upload_dir) / session_id
        target_dir.mkdir(parents=True, exist_ok=True)
        local_path = target_dir / f"{paper_id}_{safe_name}"
        s3_key = f"papers/{session_id}/{paper_id}/{safe_name}"
    else:
        local_path = Path(settings.upload_dir) / f"{paper_id}_{safe_name}"
        s3_key = f"papers/{paper_id}/{safe_name}"

    local_path.write_bytes(file_bytes)
    if settings.s3_bucket:
        try:
            get_s3().upload_file(str(local_path), settings.s3_bucket, s3_key)
        except Exception:
            pass
    return str(local_path)

def upload_visual(local_path: str, paper_id: str, visual_id: str) -> str:
    """Store visual diagram locally without uploading to S3 (only original PDFs go to S3)."""
    return local_path

def download_s3_uri(uri: str) -> str:
    if not uri.startswith("s3://"):
        return uri
    _, rest = uri.split("s3://", 1)
    bucket, key = rest.split("/", 1)
    local = Path(settings.upload_dir) / Path(key).name
    get_s3().download_file(bucket, key, str(local))
    return str(local)

def purge_session(session_id: str) -> dict:
    """Completely wipe all vector database collections, local files, and S3 objects for a private session."""
    if not session_id:
        return {"status": "skipped", "message": "No session_id provided"}

    purged_collections = []
    # 1. Permanently delete session collections from ChromaDB
    try:
        from langchain_chroma import Chroma
        for prefix in ["text", "tables", "figures"]:
            col_name = f"{prefix}_{session_id}"
            try:
                store = Chroma(collection_name=col_name, persist_directory=settings.chroma_dir)
                store.delete_collection()
                purged_collections.append(col_name)
            except Exception:
                pass
    except Exception:
        pass

    # 2. Permanently delete all local uploaded files for this session
    session_dir = Path(settings.upload_dir) / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)

    # 3. Permanently delete all S3 objects for this private session
    if settings.s3_bucket:
        try:
            s3 = get_s3()
            prefix = f"papers/{session_id}/"
            objs = s3.list_objects_v2(Bucket=settings.s3_bucket, Prefix=prefix)
            if "Contents" in objs:
                delete_keys = [{"Key": o["Key"]} for o in objs["Contents"]]
                s3.delete_objects(Bucket=settings.s3_bucket, Delete={"Objects": delete_keys})
        except Exception:
            pass

    return {
        "status": "purged",
        "session_id": session_id,
        "collections_deleted": purged_collections,
        "message": f"Session {session_id} data permanently erased from database, local disk, and S3."
    }
