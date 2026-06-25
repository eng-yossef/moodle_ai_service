import os
import shutil
import uuid
from pathlib import Path
from core.config import settings

def ensure_directories():
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def save_uploaded_file(file_bytes: bytes, original_filename: str) -> str:
    ensure_directories()
    ext = os.path.splitext(original_filename)[1]
    unique_id = uuid.uuid4().hex
    filename = f"{unique_id}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(file_bytes)
    return filepath

def delete_file(filepath: str):
    if os.path.exists(filepath):
        os.remove(filepath)