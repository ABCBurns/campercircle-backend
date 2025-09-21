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
from . import crud, schemas, auth

app = FastAPI()
Base.metadata.create_all(bind=engine)
ensure_bucket()


@app.post("/auth/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/auth/login", response_model=schemas.Token)
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token({"sub": str(db_user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserOut)
def read_me(current_user=Depends(get_current_user)):
    return current_user


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


# Standort setzen
@app.post("/location")
def update_location(
    lat: float,
    lon: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.location = from_shape(Point(lon, lat), srid=4326)
    db.commit()
    return {"msg": "Location updated"}


# Nearby-Abfrage
from sqlalchemy import func


@app.get("/nearby", response_model=list[UserOut])
def get_nearby(
    radius_km: float = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.location:
        raise HTTPException(status_code=400, detail="Set your location first")
    radius_m = radius_km * 1000
    users_with_dist = (
        db.query(
            User,
            func.ST_Distance(User.location, current_user.location).label("distance"),
        )
        .filter(
            User.id != current_user.id,
            func.ST_DWithin(User.location, current_user.location, radius_m),
        )
        .order_by("distance")
        .all()
    )
    return [u for u, dist in users_with_dist]


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
