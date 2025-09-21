from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry

from .database import Base


# -------------------------------
# User Model
# -------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    profile_image = Column(String, nullable=True)
    location = Column(Geometry("POINT", srid=4326), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sent_messages = relationship(
        "Message", back_populates="sender", foreign_keys="Message.sender_id"
    )
    received_messages = relationship(
        "Message", back_populates="receiver", foreign_keys="Message.receiver_id"
    )


# -------------------------------
# Message Model
# -------------------------------
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sender = relationship(
        "User", back_populates="sent_messages", foreign_keys=[sender_id]
    )
    receiver = relationship(
        "User", back_populates="received_messages", foreign_keys=[receiver_id]
    )
