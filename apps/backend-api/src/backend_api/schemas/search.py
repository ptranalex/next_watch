"""
Search schemas for the backend API.
"""

from typing import Any

from pydantic import BaseModel


class SearchResult(BaseModel):
    """Base class for search results."""

    id: int
    name: str
    type: str  ***REMOVED*** "movie", "actor", "genre", etc.
    image_path: str | None = None
    year: int | None = None  ***REMOVED*** For movies
    popularity: float | None = None
    additional_info: dict[str, Any] | None = None


class SearchResponse(BaseModel):
    """Response model for search endpoints."""

    suggestions: list[SearchResult]
    total: int
    page: int | None = 1
    per_page: int | None = 20
    total_pages: int | None = 1
    has_next: bool | None = False
    has_prev: bool | None = False
