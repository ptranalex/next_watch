"""
Services package for the backend API.

This package contains service classes for handling business logic and
state-changing operations, following the CQRS pattern to separate
command operations from query operations.
"""

from .movie_service import MovieService
from .user_interaction import UserInteractionService

__all__ = [
    "UserInteractionService",
    "MovieService",
]
