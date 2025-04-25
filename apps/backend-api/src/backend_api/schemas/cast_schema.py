"""
Cast schemas for API responses using Pydantic.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class CastMemberResponse(BaseModel):
    """Schema for a cast member response."""

    id: int
    tmdb_person_id: int
    name: str
    character: Optional[str] = None
    profile_path: Optional[str] = None
    order: Optional[int] = None

    class Config:
        orm_mode = True
        extra = "ignore"

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if isinstance(obj, dict):
            return cls(**obj)
        return super().model_validate(obj, **kwargs)


class CrewMemberResponse(BaseModel):
    """Schema for a crew member response."""

    id: int
    tmdb_person_id: int
    name: str
    department: Optional[str] = None
    job: Optional[str] = None
    profile_path: Optional[str] = None

    class Config:
        orm_mode = True
        extra = "ignore"

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if isinstance(obj, dict):
            return cls(**obj)
        return super().model_validate(obj, **kwargs)


class MovieCreditsResponse(BaseModel):
    """Schema for movie credits response."""

    cast: List[CastMemberResponse]
    crew: List[CrewMemberResponse]
    movie_id: int

    class Config:
        orm_mode = True
