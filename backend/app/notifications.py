from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app import models
from app.auth import get_current_user, User

class NotificationOut(BaseModel):
    id: int
    user_email: str
    title: str
    message: str
    is_read: bool
    created_at: str

    class Config:
        from_attributes = True

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[NotificationOut])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch notifications for currently logged in user
    return db.query(models.Notification).filter(
        models.Notification.user_email == current_user.email
    ).order_by(models.Notification.id.desc()).all()

@router.put("/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_email == current_user.email
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Bildirishnoma topilmadi")
    notification.is_read = True
    db.commit()
    return {"message": "O'qildi deb belgilandi"}
