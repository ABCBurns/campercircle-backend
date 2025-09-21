from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from . import models, schemas, database, auth, crud

router = APIRouter(tags=["messages"])


@router.get("/{other_user_id}", response_model=list[schemas.MessageOut])
def get_messages(
    other_user_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    return crud.get_conversation(db, current_user.id, other_user_id)


@router.post("/{other_user_id}", response_model=schemas.MessageOut)
def send_message(
    other_user_id: int,
    content: str = Body(..., embed=True, description="Message content"),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    if other_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot message yourself")

    return crud.create_message(db, current_user.id, other_user_id, content)
