import os
from pathlib import Path
from app.config import settings
from app.clients import get_s3

def ensure_dirs():
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.chroma_dir).mkdir(parents=True, exist_ok=True)

def save_upload(file_bytes: bytes, filename: str, paper_id: str) -> str:
    ensure_dirs()
    safe_name = Path(filename).name.replace(" ", "_")
    local_path = Path(settings.upload_dir) / f"{paper_id}_{safe_name}"
    local_path.write_bytes(file_bytes)
    if settings.s3_bucket:
        get_s3().upload_file(str(local_path), settings.s3_bucket, f"papers/{paper_id}/{safe_name}")
    return str(local_path)

def upload_visual(local_path: str, paper_id: str, visual_id: str) -> str:
    if not settings.s3_bucket:
        return local_path
    key = f"visuals/{paper_id}/{visual_id}.png"
    get_s3().upload_file(local_path, settings.s3_bucket, key)
    return f"s3://{settings.s3_bucket}/{key}"

def download_s3_uri(uri: str) -> str:
    if not uri.startswith("s3://"):
        return uri
    _, rest = uri.split("s3://", 1)
    bucket, key = rest.split("/", 1)
    local = Path(settings.upload_dir) / Path(key).name
    get_s3().download_file(bucket, key, str(local))
    return str(local)
