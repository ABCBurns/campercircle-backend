from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from geoalchemy2 import Geography
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    vehicle = Column(String, nullable=True)
    interests = Column(String, nullable=True)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    profile_image = Column(String, nullable=True)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
