from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db, Base

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, nullable=False)
    receiver_id = Column(Integer, nullable=False)
    sender_name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(String(50), default=str(datetime.now()))
    is_read = Column(Integer, default=0)

class MessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    sender_name: str
    content: str

class MessageOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    sender_name: str
    content: str
    created_at: str
    is_read: int
    class Config:
        from_attributes = True

router = APIRouter(prefix="/messages", tags=["Chat"])

@router.get("/", response_model=List[MessageOut])
def get_messages(
    sender_id: Optional[int] = None,
    receiver_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Message)
    if sender_id and receiver_id:
        query = query.filter(
            ((Message.sender_id == sender_id) & (Message.receiver_id == receiver_id)) |
            ((Message.sender_id == receiver_id) & (Message.receiver_id == sender_id))
        )
    elif sender_id:
        query = query.filter(Message.sender_id == sender_id)
    elif receiver_id:
        query = query.filter(Message.receiver_id == receiver_id)
    return query.order_by(Message.id).all()

@router.post("/", response_model=MessageOut, status_code=201)
def send_message(data: MessageCreate, db: Session = Depends(get_db)):
    message = Message(
        **data.model_dump(),
        created_at=str(datetime.now()),
        is_read=0
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

@router.put("/{message_id}/read")
def mark_read(message_id: int, db: Session = Depends(get_db)):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Xabar topilmadi")
    message.is_read = 1
    db.commit()
    return {"message": "O'qildi"}

@router.delete("/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Xabar topilmadi")
    db.delete(message)
    db.commit()
    return {"message": "Xabar o'chirildi"}