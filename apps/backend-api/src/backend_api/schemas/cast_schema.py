"""
Cast schemas for API responses using Pydantic.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


class CastMemberResponse(BaseModel):
    """Schema for a cast member response."""

    id: int
    actor_id: int  ***REMOVED*** This will contain the TMDB person ID
    name: str
    character: Optional[str] = None
    profile_path: Optional[str] = None
    order: Optional[int] = None
    popularity: Optional[float] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if isinstance(obj, dict):
            ***REMOVED*** Map tmdb_person_id to actor_id if dict contains tmdb_person_id
            if "tmdb_person_id" in obj and "actor_id" not in obj:
                obj = obj.copy()  ***REMOVED*** Avoid modifying the original
                obj["actor_id"] = obj.pop("tmdb_person_id")
            return cls(**obj)
        return super().model_validate(obj, **kwargs)


class CrewMemberResponse(BaseModel):
    """Schema for a crew member response."""

    id: int
    actor_id: int  ***REMOVED*** This will contain the TMDB person ID
    name: str
    department: Optional[str] = None
    job: Optional[str] = None
    profile_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if isinstance(obj, dict):
            ***REMOVED*** Map tmdb_person_id to actor_id if dict contains tmdb_person_id
            if "tmdb_person_id" in obj and "actor_id" not in obj:
                obj = obj.copy()  ***REMOVED*** Avoid modifying the original
                obj["actor_id"] = obj.pop("tmdb_person_id")
            return cls(**obj)
        return super().model_validate(obj, **kwargs)


class MovieCreditsResponse(BaseModel):
    """Schema for movie credits response."""

    cast: List[CastMemberResponse]
    crew: List[CrewMemberResponse]
    movie_id: int

    model_config = ConfigDict(from_attributes=True)


class MovieCastResponse(BaseModel):
    """Schema for movie cast response (actors only)."""

    cast: List[CastMemberResponse]
    movie_id: int

    model_config = ConfigDict(from_attributes=True)
