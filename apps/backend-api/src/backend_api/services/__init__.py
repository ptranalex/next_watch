"""
Services package for the backend API.

This package contains service classes for handling business logic and
state-changing operations, following the CQRS pattern to separate
command operations from query operations.
"""

from backend_api.services.user_interaction import UserInteractionService
from backend_api.services.movie_service import MovieService

__all__ = [
    "UserInteractionService",
    "MovieService",
]
