from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from . import auth, database, models, utils
import os

router = APIRouter(tags=["uploads"])


@router.post("/upload-profile-image")
def upload_profile_image(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    filename = f"user_{current_user.id}{ext}"
    try:
        utils.s3_client.upload_fileobj(file.file, utils.MINIO_BUCKET, filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    current_user.profile_image = (
        f"{utils.s3_client.meta.endpoint_url}/{utils.MINIO_BUCKET}/{filename}"
    )
    db.commit()
    return {"url": current_user.profile_image}
