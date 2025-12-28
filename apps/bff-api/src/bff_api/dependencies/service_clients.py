"""Service client dependencies using Fast Core's Service Client Factory.

This module configures all service clients used by the BFF API using the new
Service Client Factory system for better performance, health checking, and
lifecycle management.
"""

from typing import Any

from fast_core.dependencies.client_factory import (
    get_service_client,
    health_check_all_services,
    register_client_type,
    register_service,
)
from fast_core.dependencies.singleton import cleanup_singletons
from fastapi import Depends

from bff_api.config.app import BFFAPIConfig, settings
from bff_api.services.auth_client import AuthClient
from bff_api.services.clients.facade import BackendClient
from bff_api.services.clients.recommendation import RecommendationClient
from bff_api.services.clients.search import SearchAPIClient


def _register_all_services(config: BFFAPIConfig) -> None:
    """Register all service clients with the factory.

    Args:
        config: BFF API configuration
    """
    ***REMOVED*** Backend API - register service and custom client type
    register_service(
        name="backend",
        base_url=config.backend_api_url,
        timeout=config.backend_api_timeout,
        headers={
            "User-Agent": "NextWatch-BFF/0.1.0",
            "Authorization": f"Bearer {config.internal_api_key}",
        },
        singleton=True,  ***REMOVED*** Use singleton for performance
    )
    register_client_type("backend", BackendClient, singleton=True)

    ***REMOVED*** Auth API - register service and custom client type
    register_service(
        name="auth",
        base_url=config.auth_api_url,
        timeout=config.auth_api_timeout,
        headers={
            "User-Agent": "NextWatch-BFF/0.1.0",
            "Accept": "application/json",
        },
        singleton=True,
    )
    register_client_type("auth", AuthClient, singleton=True)

    ***REMOVED*** Recommendation API - register service and custom client type
    register_service(
        name="recommendation",
        base_url=config.reco_api_url,
        timeout=config.recommendation_api_timeout,
        headers={
            "User-Agent": "NextWatch-BFF/0.1.0",
            "Authorization": f"Bearer {config.internal_api_key}",
        },
        singleton=True,
    )
    register_client_type("recommendation", RecommendationClient, singleton=True)

    ***REMOVED*** Search API - register service and custom client type
    register_service(
        name="search",
        base_url=config.search_api_url,
        timeout=config.search_api_timeout,
        headers={
            "User-Agent": "NextWatch-BFF/0.1.0",
            "Accept": "application/json",
        },
        singleton=True,
    )
    register_client_type("search", SearchAPIClient, singleton=True)

    ***REMOVED*** ML API - optional service, only register if enabled
    if config.enable_ml_features and config.ml_api_url:
        register_service(
            name="ml",
            base_url=config.ml_api_url,
            timeout=config.ml_api_timeout,
            headers={
                "User-Agent": "NextWatch-BFF/0.1.0",
                "Authorization": f"Bearer {config.internal_api_key}",
            },
            singleton=True,
        )


***REMOVED*** Register services on module import
_register_all_services(settings)


***REMOVED*** Service client dependency functions
get_backend_client = get_service_client("backend")

get_auth_client = get_service_client("auth")

get_recommendation_client = get_service_client("recommendation")

get_search_client = get_service_client("search")


def get_ml_client(
    config: BFFAPIConfig = Depends(lambda: settings),
) -> Any:
    """Get ML client dependency.

    Returns a singleton GenericServiceClient for the ML service.
    Only available if ML features are enabled.

    Args:
        config: BFF API configuration

    Returns:
        GenericServiceClient instance for ML service

    Raises:
        ValueError: If ML features are not enabled
    """
    if not config.enable_ml_features or not config.ml_api_url:
        raise ValueError("ML features are not enabled")

    return get_service_client("ml")()


async def get_all_services_health() -> dict[str, Any]:
    """Get health status for all registered service clients.

    Returns:
        Dictionary with health status for all services
    """
    return await health_check_all_services()


async def cleanup_service_clients() -> None:
    """Clean up all service clients. Called during app shutdown."""
    await cleanup_singletons()
