from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    vehicle: Optional[str] = None
    interests: Optional[str] = None
    profile_image: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Login(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class MessageOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True
