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

SECRET_KEY = "mentoruz_secret_key_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

from app.models import User

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
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    import bcrypt
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

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu email allaqachon ro'yxatdan o'tgan")
    user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

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