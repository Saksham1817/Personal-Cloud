from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
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

def make_thumbnail(image_bytes: bytes, thumb_path: Path):
    """Creates a small preview image so listing photos is fast"""
    img = Image.open(io.BytesIO(image_bytes))
    img.thumbnail((300, 300))  # max 300x300 pixels
    img.save(thumb_path)

# --- Upload a photo ---
@router.post("/upload")
async def upload_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Only allow image files
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files allowed")

    file_bytes = await file.read()
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    # Skip duplicates
    existing = db.query(models.File).filter(
        models.File.file_hash == file_hash,
        models.File.owner_id == current_user.id
    ).first()
    if existing:
        return {"message": "Photo already uploaded", "file_id": existing.id}

    # Organize by year/month — e.g. storage/photos/2024/06/
    now = datetime.utcnow()
    month_dir = PHOTOS_DIR / str(now.year) / f"{now.month:02d}"
    month_dir.mkdir(parents=True, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    save_path = month_dir / unique_name
    thumb_path = THUMBS_DIR / f"thumb_{unique_name}"

    # Save original photo
    with open(save_path, "wb") as f:
        f.write(file_bytes)

    # Save thumbnail
    try:
        make_thumbnail(file_bytes, thumb_path)
    except Exception:
        pass  # If thumbnail fails, that's okay — photo is still saved

    # Save record to database
    db_file = models.File(
        filename=unique_name,
        original_name=file.filename,
        file_type=file.content_type,
        file_size=len(file_bytes),
        file_hash=file_hash,
        storage_path=str(save_path),
        owner_id=current_user.id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {
        "message": "Photo uploaded successfully",
        "file_id": db_file.id,
        "filename": file.filename
    }

# --- List all photos ---
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

# --- Get thumbnail ---
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