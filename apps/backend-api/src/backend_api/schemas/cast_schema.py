"""
Cast schemas for API responses using Pydantic.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict


class CastMemberResponse(BaseModel):
    """Schema for a cast member response."""

    id: int
    name: str
    character: str | None = None
    profile_path: str | None = None
    order: int | None = None
    popularity: float | None = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> "CastMemberResponse":
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
    name: str
    department: str | None = None
    job: str | None = None
    profile_path: str | None = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> "CrewMemberResponse":
        if isinstance(obj, dict):
            ***REMOVED*** Map tmdb_person_id to actor_id if dict contains tmdb_person_id
            if "tmdb_person_id" in obj and "actor_id" not in obj:
                obj = obj.copy()  ***REMOVED*** Avoid modifying the original
                obj["actor_id"] = obj.pop("tmdb_person_id")
            return cls(**obj)
        return super().model_validate(obj, **kwargs)


class MovieCreditsResponse(BaseModel):
    """Schema for movie credits response."""

    cast: list[CastMemberResponse]
    crew: list[CrewMemberResponse]
    movie_id: int

    model_config = ConfigDict(from_attributes=True)


class MovieCastResponse(BaseModel):
    """Schema for movie cast response (actors only)."""

    cast: list[CastMemberResponse]
    movie_id: int

    model_config = ConfigDict(from_attributes=True)
