"""User interaction schemas for BFF API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserMovieInteractionResponse(BaseModel):
    """Response model for user movie interactions."""

    user_id: int
    movie_id: int
    watched: bool = False
    liked: bool = False
    in_watchlist: bool = False
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class UserMovieInteractionUpdate(BaseModel):
    """Update model for user movie interactions."""

    watched: Optional[bool] = None
    liked: Optional[bool] = None
    in_watchlist: Optional[bool] = None


class ToggleInteractionRequest(BaseModel):
    """Request model for toggling a specific interaction type."""

    interaction_type: str = Field(
        ...,
        description="Type of interaction to toggle",
        pattern="^(watched|liked|in_watchlist)$",
    )


class ToggleInteractionResponse(BaseModel):
    """Response model for toggle interaction endpoint."""

    success: bool
    message: str
    interaction: UserMovieInteractionResponse
