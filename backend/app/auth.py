from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel, Field
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from app.database import get_db, Base
import bcrypt
from app.models import User
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SECRET_KEY = "mentoruz_secret_key_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)
    role: Optional[str] = "student"

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

def hash_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode(), hashed.encode())
def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token noto'g'ri")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Foydalanuvchi topilmadi")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token yaroqsiz")
        
def send_verification_email(email: str, code: str):
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = email
    msg['Subject'] = "O'rgatuvchi.uz - Email tasdiqlash"
    body = f"""
    <h2>Salom!</h2>
    <p>Tasdiqlash kodingiz: <strong style="font-size:24px">{code}</strong></p>
    <p>Kod 10 daqiqa davomida amal qiladi.</p>
    """
    msg.attach(MIMEText(body, 'html'))
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

router = APIRouter(prefix="/auth", tags=["Auth"])

verification_codes = {}

@router.post("/register", status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu email allaqachon ro'yxatdan o'tgan")
    code = str(random.randint(100000, 999999))
    verification_codes[data.email] = {
        "code": code,
        "data": data.dict()
    }
    send_verification_email(data.email, code)
    return {"message": "Email ga tasdiqlash kodi yuborildi!"}

@router.post("/verify-email")
def verify_email(email: str, code: str, db: Session = Depends(get_db)):
    if email not in verification_codes:
        raise HTTPException(status_code=400, detail="Kod topilmadi yoki muddati o'tgan")
    if verification_codes[email]["code"] != code:
        raise HTTPException(status_code=400, detail="Kod noto'g'ri")
    data = verification_codes[email]["data"]
    user = User(
        full_name=data["full_name"],
        email=data["email"],
        hashed_password=hash_password(data["password"]),
        role=data["role"]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    del verification_codes[email]
    return {"message": "Ro'yxatdan muvaffaqiyatli o'tdingiz!"}

@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email yoki parol noto'g'ri")
    token = create_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "user": user}

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
@router.put("/make-admin/{email}")
def make_admin(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Topilmadi")
    user.role = "admin"
    db.commit()
    return {"message": f"{email} admin qilindi!"}