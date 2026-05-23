from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
from typing import List, Optional
from pydantic import BaseModel, Field
from app.database import get_db, Base
from app import models

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    student_name = Column(String(100), nullable=False)
    stars = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(String(50), nullable=True)

class RatingCreate(BaseModel):
    teacher_id: int
    student_name: str
    stars: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class RatingOut(BaseModel):
    id: int
    teacher_id: int
    student_name: str
    stars: int
    comment: Optional[str]
    created_at: Optional[str]
    class Config:
        from_attributes = True

router = APIRouter(prefix="/ratings", tags=["Ratings"])

@router.get("/", response_model=List[RatingOut])
def get_ratings(teacher_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Rating)
    if teacher_id:
        query = query.filter(Rating.teacher_id == teacher_id)
    return query.all()

@router.post("/", response_model=RatingOut, status_code=201)
def create_rating(data: RatingCreate, db: Session = Depends(get_db)):
    from datetime import datetime
    # O'rtacha reytingni yangilash
    db_rating = Rating(
        teacher_id=data.teacher_id,
        student_name=data.student_name,
        stars=data.stars,
        comment=data.comment,
        created_at=str(datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    db.add(db_rating)
    db.commit()
    # O'qituvchi reytingini yangilash
    ratings = db.query(Rating).filter(Rating.teacher_id == data.teacher_id).all()
    avg = sum(r.stars for r in ratings) / len(ratings)
    teacher = db.query(models.Teacher).filter(models.Teacher.id == data.teacher_id).first()
    if teacher:
        teacher.rating = round(avg, 1)
        db.commit()
    db.refresh(db_rating)
    return db_rating

@router.get("/teacher/{teacher_id}", response_model=List[RatingOut])
def get_teacher_ratings(teacher_id: int, db: Session = Depends(get_db)):
    return db.query(Rating).filter(Rating.teacher_id == teacher_id).order_by(Rating.id.desc()).all()