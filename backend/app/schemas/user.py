"""
PhishGuard AI — User Pydantic Schemas

Defines schemas for validation of incoming request bodies and
serialization of outgoing response bodies.
"""

import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Shared fields for User schemas."""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")


class UserCreate(UserBase):
    """Fields required to register/create a new user."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password, must be at least 8 characters",
    )


class UserUpdate(BaseModel):
    """Fields allowed to be updated on a user profile."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    """Fields returned when retrieving user details."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: UserRole
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UserLogin(BaseModel):
    """Fields required to authenticate/login."""
    username_or_email: str = Field(..., description="Username or email address")
    password: str = Field(..., description="Account password")
