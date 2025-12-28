"""Service integration framework.

Provides enterprise-grade service interaction patterns including:
- HTTP client lifecycle management
- Multi-service health orchestration
- Service registry and discovery
- Retry policies with exponential backoff
"""

from .client_factory import ServiceClientFactory
from .service_registry import ServiceRegistry

__all__ = [
    "ServiceClientFactory",
    "ServiceRegistry",
]
