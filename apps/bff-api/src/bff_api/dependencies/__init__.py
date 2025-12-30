"""Shared dependencies for BFF API routes.

This module exports both fast-core service client dependencies and BFF-specific dependencies.
Now uses the new Service Client Factory for better performance and lifecycle management.
"""

# Import auth dependencies (still custom for now)
from .auth import (
    get_current_user_id,
    get_current_user_id_and_token,
    get_optional_user_id,
)

# Import service client dependencies from the new Service Client Factory module
from .service_clients import (
    cleanup_service_clients,
    get_all_services_health,
    get_auth_client,
    get_backend_client,
    get_ml_client,
    get_recommendation_client,
    get_search_client,
)

__all__ = [
    # Service client dependencies (now using Service Client Factory)
    "get_backend_client",  # Custom BackendClient via Service Client Factory
    "get_auth_client",  # Custom AuthClient via Service Client Factory
    "get_recommendation_client",  # Custom RecommendationClient via Service Client Factory
    "get_search_client",  # Custom SearchAPIClient via Service Client Factory
    "get_ml_client",  # GenericServiceClient via Service Client Factory
    # Health and lifecycle
    "get_all_services_health",
    "cleanup_service_clients",
    # Auth dependencies (custom)
    "get_current_user_id",
    "get_current_user_id_and_token",
    "get_optional_user_id",
]
