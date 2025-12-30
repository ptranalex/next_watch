"""Services package for BFF API.

Important: keep this package import side-effect free.

Tests and app code often import submodules like `bff_api.services.backend_client`.
If we eagerly import clients here, we can easily create circular imports during
FastAPI app construction and dependency wiring.

Use explicit imports from concrete modules when possible.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # Only for type checkers; avoid runtime import cycles.
    from bff_api.services.auth_client import AuthClient
    from bff_api.services.cache_service.warming.service import BFFWarmingService
    from bff_api.services.clients.facade import BackendClient
    from bff_api.services.health_service import HealthService


__all__ = [
    "BackendClient",
    "AuthClient",
    "HealthService",
    "BFFWarmingService",
]


def __getattr__(name: str) -> Any:  # pragma: no cover
    if name == "BackendClient":
        from bff_api.services.clients.facade import BackendClient

        return BackendClient
    if name == "AuthClient":
        from bff_api.services.auth_client import AuthClient

        return AuthClient
    if name == "HealthService":
        from bff_api.services.health_service import HealthService

        return HealthService
    if name == "BFFWarmingService":
        from bff_api.services.cache_service.warming.service import BFFWarmingService

        return BFFWarmingService

    raise AttributeError(name)
