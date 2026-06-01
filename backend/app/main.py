from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.teachers import router as teacher_router
from app.students import router as student_router
from app.bookings import router as booking_router
from app.auth import router as auth_router
from app.subjects import router as subject_router
from app.videos import router as video_router
from app.chat import router as chat_router
from app.tests import router as test_router
from app.ratings import router as rating_router
from app.notifications import router as notification_router
from app.database import engine, Base
from sqlalchemy import text

Base.metadata.create_all(bind=engine)

try:
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE teachers ADD COLUMN user_email VARCHAR(100)"))
except Exception:
    pass

try:
    from app.models import Subject
    from app.database import SessionLocal
    db_session = SessionLocal()
    if db_session.query(Subject).count() == 0:
        default_subjects = [
            Subject(name="Matematika", icon="📐"),
            Subject(name="Fizika", icon="⚛️"),
            Subject(name="Ona tili", icon="✍️"),
            Subject(name="Ekonometrika", icon="📊"),
            Subject(name="Adabiyot", icon="📚"),
            Subject(name="Menejment", icon="💼"),
            Subject(name="Biologiya", icon="🌱"),
            Subject(name="Iqtisodiyot", icon="🪙"),
            Subject(name="Buxgalteriya hisobi", icon="📉")
        ]
        db_session.add_all(default_subjects)
        db_session.commit()
    db_session.close()
except Exception as e:
    print("Database seeding failed:", e)

app = FastAPI(title="O'rgatuvchi.uz API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(subject_router)
app.include_router(teacher_router)
app.include_router(student_router)
app.include_router(booking_router)
app.include_router(video_router)
app.include_router(chat_router)
app.include_router(test_router)
app.include_router(rating_router)
app.include_router(notification_router)

import os

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def home():
    index_path = os.path.join(os.path.dirname(__file__), "static/index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "O'rgatuvchi.uz API v2.0 ishlayapti!"}
