from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db, Base
from app import models
from app.students import Student

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    subject = Column(String(100), nullable=False)
    lesson_type = Column(String(20), nullable=False)  # online yoki offline
    lesson_date = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")  # pending, confirmed, cancelled
    note = Column(String(255), nullable=True)
    created_at = Column(String(50), default=str(datetime.now()))

class BookingCreate(BaseModel):
    student_id: int
    teacher_id: int
    subject: str
    lesson_type: str  # "online" yoki "offline"
    lesson_date: str  # "2024-06-01 14:00"
    note: Optional[str] = None

class BookingOut(BaseModel):
    id: int
    student_id: int
    teacher_id: int
    subject: str
    lesson_type: str
    lesson_date: str
    status: str
    note: Optional[str]
    created_at: str

    class Config:
        from_attributes = True

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.get("/", response_model=List[BookingOut])
def get_bookings(
    student_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Booking)
    if student_id:
        query = query.filter(Booking.student_id == student_id)
    if teacher_id:
        query = query.filter(Booking.teacher_id == teacher_id)
    if status:
        query = query.filter(Booking.status == status)
    return query.all()

@router.post("/", response_model=BookingOut, status_code=201)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    # O'qituvchi mavjudligini tekshirish
    teacher = db.query(models.Teacher).filter(models.Teacher.id == booking.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="O'qituvchi topilmadi")
    # O'quvchi mavjudligini tekshirish
    student = db.query(Student).filter(Student.id == booking.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")
    # lesson_type tekshirish
    if booking.lesson_type not in ["online", "offline"]:
        raise HTTPException(status_code=400, detail="lesson_type faqat 'online' yoki 'offline' bo'lishi kerak")

    db_booking = Booking(
        **booking.model_dump(),
        created_at=str(datetime.now())
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Bron topilmadi")
    return booking

@router.put("/{booking_id}/status")
def update_status(booking_id: int, status: str, db: Session = Depends(get_db)):
    if status not in ["pending", "confirmed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Status noto'g'ri")
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Bron topilmadi")
    booking.status = status
    db.commit()
    db.refresh(booking)
    return {"message": f"Status '{status}' ga o'zgartirildi", "booking": booking}

@router.delete("/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Bron topilmadi")
    db.delete(booking)
    db.commit()
    return {"message": "Bron o'chirildi"}