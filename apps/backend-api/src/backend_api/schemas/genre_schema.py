"""
Genre schemas for API responses using Pydantic.
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any


class GenreBase(BaseModel):
    """Base genre fields shared across schemas."""

    name: str
    tmdb_id: Optional[int] = None


class GenreCreate(GenreBase):
    """Schema for creating a new genre."""

    pass


class GenreResponse(GenreBase):
    """Schema for genre responses including database ID."""

    id: int

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    @classmethod
    def from_orm(cls, obj):
        """Convert SQLModel object to Pydantic model, ensuring id is not None."""
        if obj.id is None:
            raise ValueError("Genre id cannot be None")
        return super().from_orm(obj)


class GenresListResponse(BaseModel):
    """Schema for genre list responses."""

    genres: List[GenreResponse]
    total: int
