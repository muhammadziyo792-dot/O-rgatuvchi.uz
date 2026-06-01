from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text
from typing import List, Optional
from pydantic import BaseModel, Field
from app.database import get_db, Base
from app import models

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    subject = Column(String(100), nullable=False)
    city = Column(String(50), nullable=True)
    bio = Column(Text, nullable=True)

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    subject: str = Field(..., min_length=2, max_length=100)
    city: Optional[str] = None
    bio: Optional[str] = None

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    subject: Optional[str] = None
    city: Optional[str] = None
    bio: Optional[str] = None

class StudentOut(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    subject: str
    city: Optional[str]
    bio: Optional[str]

    class Config:
        from_attributes = True

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/", response_model=List[StudentOut])
def get_students(
    name: Optional[str] = None,
    subject: Optional[str] = None,
    city: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Student)
    if name:
        query = query.filter(Student.name.ilike(f"%{name}%"))
    if subject:
        query = query.filter(Student.subject.ilike(f"%{subject}%"))
    if city:
        query = query.filter(Student.city.ilike(f"%{city}%"))
    return query.all()

@router.post("/", response_model=StudentOut, status_code=201)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.get("/{student_id}", response_model=StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")
    return student

@router.put("/{student_id}", response_model=StudentOut)
def update_student(student_id: int, data: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")
    db.delete(student)
    db.commit()
    return {"message": "O'quvchi o'chirildi"}