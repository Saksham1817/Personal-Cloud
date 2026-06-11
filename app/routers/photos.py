from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app import models
from PIL import Image
import hashlib, os, uuid, io
from pathlib import Path
from datetime import datetime

router = APIRouter(prefix="/photos", tags=["photos"])

PHOTOS_DIR = Path("F:/storage/photos")
THUMBS_DIR = Path("F:/storage/thumbnails")
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
THUMBS_DIR.mkdir(parents=True, exist_ok=True)

def create_thumbnail_task(file_path: str, thumb_path: str):
    """Runs in background — doesn't block the upload response"""
    try:
        with Image.open(file_path) as img:
            img.thumbnail((300, 300))
            img.save(thumb_path)
    except Exception as e:
        print(f"Thumbnail failed: {e}")

@router.post("/upload")
async def upload_photo(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files allowed")

    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"

    now = datetime.utcnow()
    month_dir = PHOTOS_DIR / str(now.year) / f"{now.month:02d}"
    month_dir.mkdir(parents=True, exist_ok=True)

    save_path = month_dir / unique_name
    thumb_path = THUMBS_DIR / f"thumb_{unique_name}"

    # Save in chunks
    file_hash = hashlib.sha256()
    file_size = 0

    with open(save_path, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            file_hash.update(chunk)
            file_size += len(chunk)

    hash_str = file_hash.hexdigest()

    # Check duplicate
    existing = db.query(models.File).filter(
        models.File.file_hash == hash_str,
        models.File.owner_id == current_user.id
    ).first()
    if existing:
        os.remove(save_path)
        return {"message": "Photo already uploaded", "file_id": existing.id}

    # Save record
    db_file = models.File(
        filename=unique_name,
        original_name=file.filename,
        file_type=file.content_type,
        file_size=file_size,
        file_hash=hash_str,
        file_category="photos",
        storage_path=str(save_path),
        owner_id=current_user.id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    # Thumbnail runs in background
    background_tasks.add_task(create_thumbnail_task, str(save_path), str(thumb_path))

    return {
        "message": "Photo uploaded successfully",
        "file_id": db_file.id,
        "filename": file.filename
    }

@router.get("/list")
def list_photos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    photos = db.query(models.File).filter(
        models.File.owner_id == current_user.id,
        models.File.file_type.like("image/%")
    ).all()
    return [
        {
            "id": p.id,
            "name": p.original_name,
            "size": p.file_size,
            "uploaded_at": p.uploaded_at
        }
        for p in photos
    ]

@router.get("/thumbnail/{file_id}")
def get_thumbnail(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    photo = db.query(models.File).filter(
        models.File.id == file_id,
        models.File.owner_id == current_user.id
    ).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    thumb_path = THUMBS_DIR / f"thumb_{photo.filename}"
    if not thumb_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not available")

    return FileResponse(path=str(thumb_path), media_type=photo.file_type)