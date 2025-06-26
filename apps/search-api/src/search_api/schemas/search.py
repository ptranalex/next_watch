"""Search schemas for the Search API.

This module contains Pydantic models for search request/response validation
based on the schemas from backend-api but adapted for the search service.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Base class for search results."""

    id: int
    name: str
    type: str = Field(..., description="Entity type: movie, actor, genre, etc.")
    image_path: Optional[str] = None
    year: Optional[int] = None  ***REMOVED*** For movies
    popularity: Optional[float] = None
    additional_info: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Response model for search endpoints."""

    suggestions: List[SearchResult] = Field(default_factory=list)
    total: int = Field(0, ge=0)
    page: Optional[int] = Field(1, ge=1)
    per_page: Optional[int] = Field(20, ge=1, le=100)
    total_pages: Optional[int] = Field(0, ge=0)
    has_next: Optional[bool] = False
    has_prev: Optional[bool] = False


class Suggestion(BaseModel):
    """Basic suggestion model."""

    id: int
    name: str
    type: str = Field(..., description="Entity type: movie, actor, genre")
    image_path: Optional[str] = None


class SuggestionsResponse(BaseModel):
    """Response model for basic suggestions."""

    suggestions: List[Suggestion] = Field(default_factory=list)
    total: int = Field(0, ge=0)


class TextSuggestion(BaseModel):
    """Enhanced text-based suggestion model."""

    text: str = Field(..., description="Suggestion text")
    type: str = Field(..., description="Entity type: movie, actor, director")
    id: Optional[int] = None
    image_path: Optional[str] = None
    year: Optional[int] = None  ***REMOVED*** Useful for movies
    popularity: Optional[float] = None
    is_partial: bool = Field(False, description="Whether this is a partial/incomplete match")
    search_type: str = Field(
        "unknown", description="How this suggestion was matched (exact, prefix, word, contains)"
    )
    additional_info: Optional[Dict[str, Any]] = None


class TextSuggestionsResponse(BaseModel):
    """Response model for enhanced text-based suggestions."""

    suggestions: List[TextSuggestion] = Field(default_factory=list)
    total: int = Field(0, ge=0)


class SearchFilters(BaseModel):
    """Search filter model for advanced search options."""

    genre_id: Optional[int] = Field(None, description="Filter by genre ID")
    actor_id: Optional[int] = Field(None, description="Filter by actor TMDB ID")
    sort_by: str = Field("title", description="Field to sort by")
    sort_desc: bool = Field(False, description="Sort in descending order")
    imdb_rating: Optional[float] = Field(None, ge=0, le=10, description="Minimum IMDb rating")
    rotten_tomatoes_rating: Optional[int] = Field(
        None, ge=0, le=100, description="Minimum RT rating"
    )
    metacritic_rating: Optional[int] = Field(
        None, ge=0, le=100, description="Minimum Metacritic rating"
    )
    year: Optional[int] = Field(None, description="Release year filter")
    start_year: Optional[int] = Field(None, description="Start year filter (inclusive)")
    end_year: Optional[int] = Field(None, description="End year filter (inclusive)")


class SearchRequest(BaseModel):
    """Request model for search operations."""

    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    page: int = Field(1, ge=1, description="Page number for pagination")
    limit: int = Field(20, ge=1, le=100, description="Number of results per page")
    filters: Optional[SearchFilters] = None
    types: Optional[List[str]] = Field(None, description="Entity types to include in search")


class SearchMetadata(BaseModel):
    """Metadata for search operations."""

    query: str
    search_type: str
    cached: bool = False
    response_time_ms: Optional[float] = None
    backend_response_time_ms: Optional[float] = None
    total_results: int = 0
    filters_applied: Optional[Dict[str, Any]] = None
