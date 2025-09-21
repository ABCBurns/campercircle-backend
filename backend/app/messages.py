from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from . import models, schemas, database, auth

router = APIRouter(tags=["messages"])


@router.get("/messages/{other_user_id}", response_model=list[schemas.MessageOut])
def get_messages(
    other_user_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    messages = (
        db.query(models.Message)
        .filter(
            (
                (models.Message.sender_id == current_user.id)
                & (models.Message.receiver_id == other_user_id)
            )
            | (
                (models.Message.sender_id == other_user_id)
                & (models.Message.receiver_id == current_user.id)
            )
        )
        .order_by(models.Message.timestamp)
        .all()
    )
    return messages


@router.post("/messages/{other_user_id}", response_model=schemas.MessageOut)
def send_message(
    other_user_id: int,
    content: str = Body(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    # Check if receiver exists
    receiver = db.query(models.User).filter(models.User.id == other_user_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")

    msg = models.Message(
        sender_id=current_user.id, receiver_id=other_user_id, content=content
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
