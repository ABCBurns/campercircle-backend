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
from .uploads import router as uploads_router
from .messages import router as messages_router

app = FastAPI()

# Initialize DB and MinIO bucket
Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def startup():
    ensure_bucket()


# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(uploads_router)
app.include_router(messages_router)
