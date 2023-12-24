from pydantic import BaseModel, EmailStr
from fastapi import UploadFile
from datetime import datetime
from typing import Optional


class Video(BaseModel):
    id: int
    blob_id: str
    title: str
    video_url: str
    thumbnail_url: str
    created_at: datetime
    user_id: int | None
    duration: float
    video_path: str
    status: str


class NewVideo(BaseModel):
    blob_base: str


class SendVideo(BaseModel):
    id: int
    email: EmailStr


class User(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str


class CreateUser(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class VerifyUser(BaseModel):
    user_id: int
    otp_code: str


class UserOut(BaseModel):
    message: str
    user: User | None


class TokenData(BaseModel):
    id: Optional[str]


class Token(BaseModel):
    access_token: str
    token_type: str
