"""Dependencies module for Fast Core."""

from .auth import get_current_user, get_optional_user, require_auth
from .cache import get_cache_manager, get_cache_service, get_cache_provider, get_redis_client
from .database import get_db_session, get_database_service, get_database_engine
from .common import get_pagination, get_request_id, get_search_params, get_settings
from .context import (
    get_current_request_context,
    get_current_request_id,
    get_current_trace_headers,
    require_request_context,
    require_request_id,
    get_trace_context_injector,
)
from .singleton import (
    get_singleton_client,
    register_singleton,
    get_singleton,
    cleanup_singletons,
    singleton_lifespan,
    create_singleton_dependency,
    SingletonConfig,
    SingletonManager,
)
from .client_factory import (
    ServiceClientConfig,
    BaseServiceClient,
    GenericServiceClient,
    ServiceClientFactory,
    register_service,
    register_client_type,
    get_service_client,
    create_service_client,
    list_services,
    health_check_all_services,
    get_service_factory,
    service_client,
)

__all__ = [
    ***REMOVED*** Auth dependencies
    "get_current_user",
    "get_optional_user",
    "require_auth",
    ***REMOVED*** Cache dependencies
    "get_cache_manager",
    "get_cache_service",
    "get_cache_provider",
    "get_redis_client",
    ***REMOVED*** Database dependencies
    "get_db_session",
    "get_database_service",
    "get_database_engine",
    ***REMOVED*** Common dependencies
    "get_pagination",
    "get_request_id",
    "get_search_params",
    "get_settings",
    ***REMOVED*** Context dependencies
    "get_current_request_context",
    "get_current_request_id",
    "get_current_trace_headers",
    "require_request_context",
    "require_request_id",
    "get_trace_context_injector",
    ***REMOVED*** Singleton dependencies
    "get_singleton_client",
    "register_singleton",
    "get_singleton",
    "cleanup_singletons",
    "singleton_lifespan",
    "create_singleton_dependency",
    "SingletonConfig",
    "SingletonManager",
    ***REMOVED*** Service client factory
    "ServiceClientConfig",
    "BaseServiceClient",
    "GenericServiceClient",
    "ServiceClientFactory",
    "register_service",
    "register_client_type",
    "get_service_client",
    "create_service_client",
    "list_services",
    "health_check_all_services",
    "get_service_factory",
    "service_client",
]
