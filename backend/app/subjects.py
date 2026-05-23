from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
from typing import List, Optional
from pydantic import BaseModel, Field
from app.database import get_db, Base

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    icon = Column(String(50), nullable=True)

class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    icon: Optional[str] = None

class SubjectOut(BaseModel):
    id: int
    name: str
    icon: Optional[str]
    class Config:
        from_attributes = True

router = APIRouter(prefix="/subjects", tags=["Subjects"])

@router.get("/", response_model=List[SubjectOut])
def get_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).all()

@router.post("/", response_model=SubjectOut, status_code=201)
def create_subject(data: SubjectCreate, db: Session = Depends(get_db)):
    existing = db.query(Subject).filter(Subject.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu fan allaqachon mavjud")
    subject = Subject(**data.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

@router.delete("/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Fan topilmadi")
    db.delete(subject)
    db.commit()
    return {"message": "Fan o'chirildi"}