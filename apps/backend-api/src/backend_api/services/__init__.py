"""
Services package for the backend API.

This package contains service classes for handling business logic and
state-changing operations, following the CQRS pattern to separate
command operations from query operations.
"""

from .health_service import HealthService, close_health_service, get_health_service
from .movie_service import MovieService
from .user_interaction import UserInteractionService

# Optional services
try:
    from .suggestion_engine import SuggestionEngine  # noqa: F401

    _suggestion_engine_available = True
except ImportError:
    _suggestion_engine_available = False

__all__ = [
    "UserInteractionService",
    "MovieService",
    "HealthService",
    "get_health_service",
    "close_health_service",
]

if _suggestion_engine_available:
    __all__.append("SuggestionEngine")
