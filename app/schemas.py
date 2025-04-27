from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr


# User schema ------------------


class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserRegister(UserBase):
    name: str
    pass


class UserLogin(UserBase):
    pass


class User(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    profile_img: Optional[str] = ""
    user_type: Optional[str] = "email"
    created_at: datetime

    model_config = {"from_attributes": True, "json_encoders": {UUID: lambda v: str(v)}}


class UserEdit(BaseModel):
    name: str
    profile_img: Optional[str] = ""
    user_type: str


class UserOut(BaseModel):
    user: User


class UserAuthOut(BaseModel):
    access_token: str
    token_type: str
    user: User


class ChangePassword(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str


class ChangePasswordOut(BaseModel):
    success: bool
    message: str


# Task schema------------------


class TaskBase(BaseModel):
    title: str
    details: str
    team_members: Optional[List[str]] = []
    date: str
    time: str


class TaskCreate(TaskBase):
    owner_id: Optional[str] = ""
    pass


class TaskUpdate(TaskBase):
    pass


class Task(BaseModel):
    id: UUID
    owner_id: str
    title: str
    details: str
    team_members: Optional[List[str]] = []
    date: str
    time: str
    is_completed: Optional[bool] = False
    created_at: datetime

    model_config = {"from_attributes": True, "json_encoders": {UUID: lambda v: str(v)}}


# JWT Token schema------------------


class TokenData(BaseModel):
    id: Optional[UUID] = None


class Token(BaseModel):
    access_token: str
    token_type: str


# Pagination schema------------------


class PaginatedUsers(BaseModel):
    users: List[User]
    total_count: int
    next_cursor: Optional[UUID]


# Otp schema------------------


class OtpOut(BaseModel):
    otp: str
    message: str


class Otp(BaseModel):
    email: EmailStr


# Pdf schema------------------


class ExtractionResult(BaseModel):
    filename: str
    text: str | None = None  # Optional text field
    error: str | None = None
