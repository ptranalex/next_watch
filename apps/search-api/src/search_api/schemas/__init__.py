"""Search API schemas package.

This module contains Pydantic models for request/response validation
and data serialization for the Search API.
"""

from .search import (
    SearchResponse,
    SearchResult,
    Suggestion,
    SuggestionsResponse,
    TextSuggestion,
    TextSuggestionsResponse,
)

__all__ = [
    "SearchResponse",
    "SearchResult",
    "Suggestion",
    "SuggestionsResponse",
    "TextSuggestion",
    "TextSuggestionsResponse",
]
