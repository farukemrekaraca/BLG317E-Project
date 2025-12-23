from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    name: str
    mail_address: EmailStr
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    password: str
    type_id: int = 4  # Default to Attendee


class UserLogin(BaseModel):
    mail_address: EmailStr
    password: str


class UserResponse(UserBase):
    user_id: int
    type_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
