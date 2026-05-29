from sqlalchemy import Column, Integer, String, Float, Text, Boolean
from app.database import Base

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    experience = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    phone = Column(String(20), nullable=True)
    bio = Column(Text, nullable=True)
    rating = Column(Float, default=0.0)
    city = Column(String(50), nullable=True)
    university = Column(String(200), nullable=True)
    degree_type = Column(String(100), nullable=True)
    degree_year = Column(Integer, nullable=True)
    certificate_info = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    status = Column(String(20), default="pending")

    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(20), default="student")
    is_active = Column(Boolean, default=True)