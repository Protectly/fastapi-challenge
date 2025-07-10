from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @validator("username")
    def username_must_be_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return v

    @validator("password")
    def password_must_be_valid(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
