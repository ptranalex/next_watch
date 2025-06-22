"""Shared dependencies for BFF API routes.

This module exports both fast-core service client dependencies and BFF-specific dependencies.
Now uses the new Service Client Factory for better performance and lifecycle management.
"""

***REMOVED*** Import auth dependencies (still custom for now)
from .auth import get_current_user_id, get_current_user_id_and_token, get_optional_user_id

***REMOVED*** Import service client dependencies from the new Service Client Factory module
from .service_clients import (
    get_backend_client,
    get_auth_client,
    get_recommendation_client,
    get_ml_client,
    get_all_services_health,
    cleanup_service_clients,
)

__all__ = [
    ***REMOVED*** Service client dependencies (now using Service Client Factory)
    "get_backend_client",  ***REMOVED*** Custom BackendClient via Service Client Factory
    "get_auth_client",  ***REMOVED*** GenericServiceClient via Service Client Factory
    "get_recommendation_client",  ***REMOVED*** GenericServiceClient via Service Client Factory
    "get_ml_client",  ***REMOVED*** GenericServiceClient via Service Client Factory
    ***REMOVED*** Health and lifecycle
    "get_all_services_health",
    "cleanup_service_clients",
    ***REMOVED*** Auth dependencies (custom)
    "get_current_user_id",
    "get_current_user_id_and_token",
    "get_optional_user_id",
]
