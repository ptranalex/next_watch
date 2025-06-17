"""
Search schemas for the backend API.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SearchResult(BaseModel):
    """Base class for search results."""

    id: int
    name: str
    type: str  ***REMOVED*** "movie", "actor", "genre", etc.
    image_path: Optional[str] = None
    year: Optional[int] = None  ***REMOVED*** For movies
    popularity: Optional[float] = None
    additional_info: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Response model for search endpoints."""

    suggestions: List[SearchResult]
    total: int
    page: Optional[int] = 1
    per_page: Optional[int] = 20
    total_pages: Optional[int] = 1
    has_next: Optional[bool] = False
    has_prev: Optional[bool] = False
