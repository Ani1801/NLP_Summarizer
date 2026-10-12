from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(default="Lawyer")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class GoogleToken(BaseModel):
    """Request body for POST /api/auth/google — contains the credential from Google Identity Services."""
    credential: str

class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    role: Optional[str] = Field(None)

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)
