"""Authentication schemas for BFF API."""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login request model."""

    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """User registration request model."""

    email: EmailStr
    password: str
    name: str | None = None


class TokenResponse(BaseModel):
    """Authentication token response model."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""

    refresh_token: str


class UserResponse(BaseModel):
    """User information response model."""

    id: int
    email: str
    name: str | None = None
    is_active: bool
    created_at: str


class AuthenticatedUserResponse(BaseModel):
    """Response for successful authentication including user info."""

    user: UserResponse
    tokens: TokenResponse


class TokenVerificationResponse(BaseModel):
    """Token verification response model."""

    valid: bool
    user_id: int | None = None
    email: str | None = None
    message: str | None = None
