"""Services package for BFF API application.

This package provides client implementations for communicating with backend
services. These clients encapsulate the HTTP communication, error handling,
retries, and response processing for all backend service interactions.

Key components:
- BackendClient: Client for the main Backend API service
- AuthClient: Client for the authentication service

The clients implement resilient communication with:
- Automatic retries with exponential backoff
- Consistent error handling
- Async communication for optimal performance
- Comprehensive logging

See the README.md file in this directory for detailed documentation.
"""

from .backend_client import BackendClient
from .auth_client import AuthClient

__all__ = ["BackendClient", "AuthClient"]
