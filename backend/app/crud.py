from sqlalchemy.orm import Session
from . import models, schemas
from .security import get_password_hash


# -------------------------------
# User CRUD
# -------------------------------
def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        profile_image=None,
        location=None,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# -------------------------------
# Message CRUD
# -------------------------------
def create_message(
    db: Session, sender_id: int, receiver_id: int, content: str
) -> models.Message:
    msg = models.Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_conversation(db: Session, user1_id: int, user2_id: int) -> list[models.Message]:
    return (
        db.query(models.Message)
        .filter(
            (
                (models.Message.sender_id == user1_id)
                & (models.Message.receiver_id == user2_id)
            )
            | (
                (models.Message.sender_id == user2_id)
                & (models.Message.receiver_id == user1_id)
            )
        )
        .order_by(models.Message.timestamp)
        .all()
    )
