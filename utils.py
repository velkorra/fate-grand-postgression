import os
import shutil
from pathlib import Path

MEDIA_DIR = Path("media") / "servants"
SKILL_DIR = Path("media") / "skills"
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(SKILL_DIR, exist_ok=True)

def save_file_to_disk(upload_file, path: Path):
    os.makedirs(path.parent, exist_ok=True)
    
    with open(path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return str(path)