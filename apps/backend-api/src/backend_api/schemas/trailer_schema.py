"""
Trailer schemas for API responses using Pydantic.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class TrailerBase(BaseModel):
    """Base trailer fields shared across schemas."""

    youtube_key: str
    name: str
    is_official: bool
    url_link: str | None = None


class TrailerCreate(TrailerBase):
    """Schema for creating a new trailer."""

    movie_id: int


class TrailerResponse(TrailerBase):
    """Schema for trailer responses including database ID."""

    id: int
    movie_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> "TrailerResponse":
        if isinstance(obj, dict):
            return cls(**obj)
        return super().model_validate(obj, **kwargs)
