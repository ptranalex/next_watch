"""Search API service layer.

This module contains services for handling search operations,
external API communications, and business logic.
"""

from .backend_client import BackendAPIClient
from .search_service import SearchService
from .suggestion_engine import SuggestionEngine

__all__ = [
    "BackendAPIClient",
    "SearchService",
    "SuggestionEngine",
]
