"""
Dependencies module for the backend API.

This module provides FastAPI dependency functions for request handling.
"""

from .user_context import get_user_id_from_header

__all__ = ["get_user_id_from_header"]
