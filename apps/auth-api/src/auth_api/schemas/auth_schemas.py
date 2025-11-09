"""
Authentication schema definitions for dedicated auth service.
"""

from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str | None = None


class UserCreate(UserBase):
    """User registration schema."""

    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v: str, info: Any) -> str:
        """Validate that passwords match."""
        if "password" in info.data and v != info.data["password"]:
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

        from_attributes = True


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
    user_id: int | None = None
    email: str | None = None
    username: str | None = None
    error: str | None = None
