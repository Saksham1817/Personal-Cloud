from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app import models
import hashlib, shutil, os, uuid
from pathlib import Path

router = APIRouter(prefix="/files", tags=["files"])

PHOTOS_DIR = Path("F:/storage/photos")
VIDEOS_DIR = Path("F:/storage/videos")
AUDIO_DIR = Path("F:/storage/audio")
DOCS_DIR = Path("F:/storage/documents")
OTHERS_DIR = Path("F:/storage/others")

for d in [PHOTOS_DIR, VIDEOS_DIR, AUDIO_DIR, DOCS_DIR, OTHERS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def get_storage_dir(content_type: str) -> Path:
    if not content_type:
        return OTHERS_DIR
    if content_type.startswith("image/"):
        return PHOTOS_DIR
    if content_type.startswith("video/"):
        return VIDEOS_DIR
    if content_type.startswith("audio/"):
        return AUDIO_DIR
    if any(x in content_type for x in [
        "pdf", "msword", "wordprocessingml",
        "ms-excel", "spreadsheetml",
        "text/plain", "powerpoint", "presentationml"
    ]):
        return DOCS_DIR
    return OTHERS_DIR

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    ext = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4()}{ext}"
    storage_dir = get_storage_dir(file.content_type)
    save_path = storage_dir / unique_name

    ct = file.content_type or ""
    if ct.startswith("image/"): category = "photos"
    elif ct.startswith("video/"): category = "videos"
    elif ct.startswith("audio/"): category = "audio"
    elif any(x in ct for x in ["pdf","msword","wordprocessingml","ms-excel","spreadsheetml","text/plain","powerpoint"]): category = "documents"
    else: category = "others"

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

    existing = db.query(models.File).filter(
        models.File.file_hash == hash_str,
        models.File.owner_id == current_user.id
    ).first()
    if existing:
        os.remove(save_path)
        return {"message": "File already exists", "file_id": existing.id}

    db_file = models.File(
        filename=unique_name,
        original_name=file.filename,
        file_type=file.content_type,
        file_size=file_size,
        file_hash=hash_str,
        file_category=category,
        storage_path=str(save_path),
        owner_id=current_user.id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {
        "message": "Uploaded successfully",
        "file_id": db_file.id,
        "filename": file.filename,
        "size": file_size
    }

@router.get("/list")
def list_files(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    files = db.query(models.File).filter(models.File.owner_id == current_user.id).all()
    return [
        {
            "id": f.id,
            "name": f.original_name,
            "type": f.file_type,
            "size": f.file_size,
            "category": f.file_category,
            "uploaded_at": f.uploaded_at
        }
        for f in files
    ]

@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    file = db.query(models.File).filter(
        models.File.id == file_id,
        models.File.owner_id == current_user.id
    ).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file.storage_path,
        filename=file.original_name,
        media_type=file.file_type
    )

@router.delete("/delete/{file_id}")
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    file = db.query(models.File).filter(
        models.File.id == file_id,
        models.File.owner_id == current_user.id
    ).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if os.path.exists(file.storage_path):
        os.remove(file.storage_path)

    db.delete(file)
    db.commit()

    return {"message": "File deleted successfully"}

@router.get("/storage-stats")
def storage_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    disk = shutil.disk_usage("F:/")
    user_files = db.query(models.File).filter(models.File.owner_id == current_user.id).all()
    user_used = sum(f.file_size or 0 for f in user_files)
    user_count = len(user_files)

    return {
        "disk_total": disk.total,
        "disk_used": disk.used,
        "disk_free": disk.free,
        "user_used": user_used,
        "user_files": user_count,
        "percent_used": round((disk.used / disk.total) * 100, 1)
    }

@router.get("/direct/{file_id}/{filename}")
def direct_download(
    file_id: int,
    filename: str,
    token: str,
    db: Session = Depends(get_db)
):
    from app.auth import SECRET_KEY, ALGORITHM
    from jose import jwt, JWTError
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    file = db.query(models.File).filter(
        models.File.id == file_id,
        models.File.owner_id == user.id
    ).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file.storage_path,
        filename=file.original_name,
        media_type=file.file_type
    )

@router.get("/list/{category}")
def list_by_category(
    category: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    files = db.query(models.File).filter(
        models.File.owner_id == current_user.id,
        models.File.file_category == category
    ).all()
    return [
        {
            "id": f.id,
            "name": f.filename,
            "type": f.file_type,
            "size": f.file_size,
            "category": f.file_category,
            "uploaded_at": f.uploaded_at
        }
        for f in files
    ]