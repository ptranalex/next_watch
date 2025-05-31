"""Shared dependencies for BFF API routes."""

from .common import get_backend_client, get_auth_client

__all__ = ["get_backend_client", "get_auth_client"] 