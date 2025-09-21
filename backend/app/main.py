from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
from .database import get_db, Base, engine
from .models import User, Message
from .schemas import UserOut, MessageOut
from .auth import get_current_user
from .utils import s3_client, MINIO_BUCKET, ensure_bucket
import os
from . import schemas

from .auth import router as auth_router
from .users import router as users_router

app = FastAPI()

# Initialize DB and MinIO bucket
Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def startup():
    ensure_bucket()


# Include routers
app.include_router(auth_router)
app.include_router(users_router)


# Profilbild Upload
@app.post("/upload-profile-image")
def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    filename = f"user_{current_user.id}{ext}"
    s3_client.upload_fileobj(file.file, MINIO_BUCKET, filename)
    current_user.profile_image = (
        f"{s3_client.meta.endpoint_url}/{MINIO_BUCKET}/{filename}"
    )
    db.commit()
    return {"url": current_user.profile_image}


# Chat abrufen
@app.get("/messages/{other_user_id}", response_model=list[MessageOut])
def get_messages(
    other_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    messages = (
        db.query(Message)
        .filter(
            (
                (Message.sender_id == current_user.id)
                & (Message.receiver_id == other_user_id)
            )
            | (
                (Message.sender_id == other_user_id)
                & (Message.receiver_id == current_user.id)
            )
        )
        .order_by(Message.timestamp)
        .all()
    )
    return messages


# Nachricht senden
from fastapi import Body


@app.post("/messages/{other_user_id}", response_model=MessageOut)
def send_message(
    other_user_id: int,
    content: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    msg = Message(sender_id=current_user.id, receiver_id=other_user_id, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
