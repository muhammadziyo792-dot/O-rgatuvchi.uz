from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db, Base

class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    title = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(String(300), nullable=False)
    option_b = Column(String(300), nullable=False)
    option_c = Column(String(300), nullable=False)
    option_d = Column(String(300), nullable=False)
    correct_answer = Column(String(1), nullable=False)  # a, b, c, d

class QuestionCreate(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str

class QuestionOut(BaseModel):
    id: int
    test_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    class Config:
        from_attributes = True

class TestCreate(BaseModel):
    teacher_id: int
    title: str
    subject: Optional[str] = None
    description: Optional[str] = None
    questions: Optional[List[QuestionCreate]] = []

class TestOut(BaseModel):
    id: int
    teacher_id: int
    title: str
    subject: Optional[str]
    description: Optional[str]
    class Config:
        from_attributes = True

class TestDetail(BaseModel):
    id: int
    teacher_id: int
    title: str
    subject: Optional[str]
    description: Optional[str]
    questions: List[QuestionOut] = []
    class Config:
        from_attributes = True

class AnswerSubmit(BaseModel):
    answers: dict  # {question_id: "a"/"b"/"c"/"d"}

router = APIRouter(prefix="/tests", tags=["Tests"])

@router.get("/", response_model=List[TestOut])
def get_tests(teacher_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Test)
    if teacher_id:
        query = query.filter(Test.teacher_id == teacher_id)
    return query.all()

@router.post("/", response_model=TestOut, status_code=201)
def create_test(data: TestCreate, db: Session = Depends(get_db)):
    test = Test(
        teacher_id=data.teacher_id,
        title=data.title,
        subject=data.subject,
        description=data.description
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    for q in data.questions:
        question = Question(test_id=test.id, **q.model_dump())
        db.add(question)
    db.commit()
    return test

@router.get("/{test_id}", response_model=TestDetail)
def get_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test topilmadi")
    questions = db.query(Question).filter(Question.test_id == test_id).all()
    return {
        "id": test.id,
        "teacher_id": test.teacher_id,
        "title": test.title,
        "subject": test.subject,
        "description": test.description,
        "questions": questions
    }

@router.post("/{test_id}/submit")
def submit_test(test_id: int, data: AnswerSubmit, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.test_id == test_id).all()
    if not questions:
        raise HTTPException(status_code=404, detail="Test topilmadi")
    correct = 0
    total = len(questions)
    results = []
    for q in questions:
        user_answer = data.answers.get(str(q.id), "")
        is_correct = user_answer.lower() == q.correct_answer.lower()
        if is_correct:
            correct += 1
        results.append({
            "question_id": q.id,
            "question": q.question_text,
            "your_answer": user_answer,
            "correct_answer": q.correct_answer,
            "is_correct": is_correct
        })
    return {
        "total": total,
        "correct": correct,
        "score": round(correct / total * 100, 1),
        "results": results
    }

@router.delete("/{test_id}")
def delete_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test topilmadi")
    db.query(Question).filter(Question.test_id == test_id).delete()
    db.delete(test)
    db.commit()
    return {"message": "Test o'chirildi"}
    