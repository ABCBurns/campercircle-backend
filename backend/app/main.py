from fastapi import FastAPI
from .database import Base, engine
from .auth import router as auth_router
from .users import router as users_router
from .messages import router as messages_router
from .uploads import router as uploads_router
from .utils import ensure_bucket

app = FastAPI(title="CamperCircle App API")

app = FastAPI()

# Initialize DB and MinIO bucket
Base.metadata.create_all(bind=engine)
ensure_bucket()

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(uploads_router)
app.include_router(messages_router)
