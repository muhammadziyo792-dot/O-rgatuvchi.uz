from pydantic import BaseModel, Field
from typing import Optional

class TeacherCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    subject: str = Field(..., min_length=2, max_length=100)
    experience: int = Field(..., ge=0, le=50)
    price: int = Field(..., ge=0)
    phone: Optional[str] = None
    bio: Optional[str] = None
    city: Optional[str] = None
    university: Optional[str] = None
    degree_type: Optional[str] = None
    degree_year: Optional[int] = None
    certificate_info: Optional[str] = None
    user_email: Optional[str] = None

class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    experience: Optional[int] = None
    price: Optional[int] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    city: Optional[str] = None
    university: Optional[str] = None
    degree_type: Optional[str] = None
    degree_year: Optional[int] = None
    certificate_info: Optional[str] = None

class TeacherOut(BaseModel):
    id: int
    name: str
    subject: str
    experience: int
    price: int
    phone: Optional[str]
    bio: Optional[str]
    rating: float
    city: Optional[str]
    university: Optional[str]
    degree_type: Optional[str]
    degree_year: Optional[int]
    certificate_info: Optional[str]
    is_verified: bool
    status: str
    user_email: Optional[str]

    class Config:
        from_attributes = True