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
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

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

app.mount("/static", StaticFiles(directory="../Frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("../Frontend/index.html")