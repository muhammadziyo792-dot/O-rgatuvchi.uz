from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas
from app.database import get_db
from app.auth import get_current_user, User

router = APIRouter(prefix="/teachers", tags=["Teachers"])

@router.get("/", response_model=List[schemas.TeacherOut])
def get_teachers(
    subject: Optional[str] = None,
    city: Optional[str] = None,
    max_price: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Teacher).filter(models.Teacher.is_verified == True)
    if subject:
        query = query.filter(models.Teacher.subject.ilike(f"%{subject}%"))
    if city:
        query = query.filter(models.Teacher.city.ilike(f"%{city}%"))
    if max_price:
        query = query.filter(models.Teacher.price <= max_price)
    return query.all()

@router.get("/pending", response_model=List[schemas.TeacherOut])
def get_pending(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Faqat admin uchun!")
    return db.query(models.Teacher).filter(models.Teacher.is_verified == False).all()

@router.post("/", response_model=schemas.TeacherOut, status_code=201)
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    db_teacher = models.Teacher(**teacher.model_dump())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@router.get("/{teacher_id}", response_model=schemas.TeacherOut)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="O'qituvchi topilmadi")
    return teacher

@router.put("/{teacher_id}", response_model=schemas.TeacherOut)
def update_teacher(teacher_id: int, data: schemas.TeacherUpdate, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="O'qituvchi topilmadi")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(teacher, field, value)
    db.commit()
    db.refresh(teacher)
    return teacher

@router.put("/{teacher_id}/verify")
def verify_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Faqat admin uchun!")
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="O'qituvchi topilmadi")
    teacher.is_verified = True
    teacher.status = "verified"
    db.commit()
    return {"message": "Tasdiqlandi"}

@router.put("/{teacher_id}/reject")
def reject_teacher(
    teacher_id: int,
    reason: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Faqat admin uchun!")
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="O'qituvchi topilmadi")
    teacher.is_verified = False
    teacher.status = "rejected"
    db.commit()
    return {"message": "Rad etildi"}

@router.delete("/{teacher_id}")
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Faqat admin uchun!")
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="O'qituvchi topilmadi")
    db.delete(teacher)
    db.commit()
    return {"message": "O'qituvchi o'chirildi"}