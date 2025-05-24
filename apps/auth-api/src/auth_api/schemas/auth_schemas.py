"""
Authentication schema definitions for dedicated auth service.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: Optional[str] = None


class UserCreate(UserBase):
    """User registration schema."""

    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)

    @validator("password_confirm")
    def passwords_match(cls, v, values):
        """Validate that passwords match."""
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response schema."""

    id: int

    class Config:
        """Pydantic config."""

        orm_mode = True


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: str  ***REMOVED*** user id
    exp: int  ***REMOVED*** expiration time
    iat: int  ***REMOVED*** issued at time
    type: str  ***REMOVED*** token type


class RefreshToken(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class TokenVerificationRequest(BaseModel):
    """Token verification request schema for BFF to validate tokens."""

    token: str


class TokenVerificationResponse(BaseModel):
    """Token verification response schema containing user info."""

    valid: bool
    user_id: Optional[int] = None
    email: Optional[str] = None
    username: Optional[str] = None
    error: Optional[str] = None
