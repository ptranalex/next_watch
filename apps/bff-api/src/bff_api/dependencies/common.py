"""Common dependencies for BFF API routes."""

from fastapi import Request
from bff_api.services.backend_client import BackendClient
from bff_api.services.auth_client import AuthClient


def get_backend_client(request: Request) -> BackendClient:
    """Dependency to get backend client from app state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Shared backend client instance
        
    Raises:
        AttributeError: If backend client is not initialized in app state
    """
    return request.app.state.backend_client


def get_auth_client(request: Request) -> AuthClient:
    """Dependency to get auth client from app state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Shared auth client instance
        
    Raises:
        AttributeError: If auth client is not initialized in app state
    """
    return request.app.state.auth_client 