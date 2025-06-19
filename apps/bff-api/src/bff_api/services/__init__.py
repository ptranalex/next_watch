"""Services package for BFF API application.

This package provides client implementations for communicating with backend
services. These clients encapsulate the HTTP communication, error handling,
retries, and response processing for all backend service interactions.

Key components:
- BackendClient: Client for the main Backend API service
- AuthClient: Client for the authentication service
- HealthService: Health monitoring for all external dependencies

The clients implement resilient communication with:
- Automatic retries with exponential backoff
- Consistent error handling
- Async communication for optimal performance
- Comprehensive logging

See the README.md file in this directory for detailed documentation.
"""

from bff_api.services.auth_client import AuthClient
from bff_api.services.clients.facade import BackendClient
from bff_api.services.health_service import HealthService, close_health_service, get_health_service
from bff_api.services.cache_service import (
    BFFWarmingService,
    configure_bff_warming,
    get_bff_warming_config,
    get_bff_warming_service,
)

__all__ = [
    "BackendClient",
    "AuthClient",
    "HealthService",
    "get_health_service",
    "close_health_service",
    "BFFWarmingService",
    "get_bff_warming_service",
    "configure_bff_warming",
    "get_bff_warming_config",
]
