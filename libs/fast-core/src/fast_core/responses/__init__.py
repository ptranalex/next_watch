"""Response utilities for consistent API responses.

This module provides utilities for creating consistent, well-structured API responses
across different services and domains. It includes patterns for pagination, detail views,
search results, collections, and error responses.
"""

from .builder import ResponseBuilder
from .types import (
    PaginatedResponse,
    DetailResponse,
    CollectionResponse,
    SearchResponse,
    ActionResponse,
    ErrorResponse,
)

__all__ = [
    "ResponseBuilder",
    "PaginatedResponse",
    "DetailResponse",
    "CollectionResponse",
    "SearchResponse",
    "ActionResponse",
    "ErrorResponse",
]
