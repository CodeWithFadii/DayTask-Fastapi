from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


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
    email: str
    name: str
    profile_img: Optional[str] = "null"
    user_type: Optional[str] = "email"
    created_at: datetime

    model_config = {"from_attributes": True, "json_encoders": {UUID: lambda v: str(v)}}


class UserOut(BaseModel):
    user: User


class UserAuthOut(BaseModel):
    access_token: str
    token_type: str
    user: User
    
    
class ChangePassword(BaseModel):
    email: EmailStr
    old_password: str
    new_password:str
    
class ChangePasswordOut(BaseModel):
    success: bool
    message: str


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
