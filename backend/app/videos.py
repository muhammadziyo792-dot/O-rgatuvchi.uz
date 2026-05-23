from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db, Base

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    youtube_url = Column(String(500), nullable=True)
    file_url = Column(String(500), nullable=True)
    subject = Column(String(100), nullable=True)

class VideoCreate(BaseModel):
    teacher_id: int
    title: str
    description: Optional[str] = None
    youtube_url: Optional[str] = None
    file_url: Optional[str] = None
    subject: Optional[str] = None

class VideoOut(BaseModel):
    id: int
    teacher_id: int
    title: str
    description: Optional[str]
    youtube_url: Optional[str]
    file_url: Optional[str]
    subject: Optional[str]
    class Config:
        from_attributes = True

router = APIRouter(prefix="/videos", tags=["Videos"])

@router.get("/", response_model=List[VideoOut])
def get_videos(teacher_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Video)
    if teacher_id:
        query = query.filter(Video.teacher_id == teacher_id)
    return query.all()

@router.post("/", response_model=VideoOut, status_code=201)
def create_video(data: VideoCreate, db: Session = Depends(get_db)):
    if not data.youtube_url and not data.file_url:
        raise HTTPException(status_code=400, detail="YouTube link yoki fayl URL kerak")
    video = Video(**data.model_dump())
    db.add(video)
    db.commit()
    db.refresh(video)
    return video

@router.delete("/{video_id}")
def delete_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video topilmadi")
    db.delete(video)
    db.commit()
    return {"message": "Video o'chirildi"}