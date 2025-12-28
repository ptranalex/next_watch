"""Fast Core - FastAPI Framework Extensions.

A comprehensive framework for building production-ready FastAPI applications
with enhanced dependency injection, error handling, middleware, and more.
"""

from .app import AppOptions, create_app
from .clients import ServiceClient, ServiceConfig
from .config import FastAPIConfig, FastAPIConfigMixin
from .dependencies import (
    BaseServiceClient,
    GenericServiceClient,
    ***REMOVED*** Service client factory
    ServiceClientConfig,
    ServiceClientFactory,
    SingletonConfig,
    SingletonManager,
    cleanup_singletons,
    create_service_client,
    create_singleton_dependency,
    ***REMOVED*** Cache dependencies
    get_cache_manager,
    get_cache_provider,
    get_cache_service,
    ***REMOVED*** Context dependencies
    get_current_request_context,
    get_current_request_id,
    get_current_trace_headers,
    ***REMOVED*** Auth dependencies
    get_current_user,
    get_database_engine,
    get_database_service,
    ***REMOVED*** Database dependencies
    get_db_session,
    get_optional_user,
    ***REMOVED*** Common dependencies
    get_pagination,
    get_redis_client,
    get_request_id,
    get_search_params,
    get_service_client,
    get_service_factory,
    get_settings,
    get_singleton,
    ***REMOVED*** Singleton dependencies
    get_singleton_client,
    get_trace_context_injector,
    health_check_all_services,
    list_services,
    register_client_type,
    register_service,
    register_singleton,
    require_auth,
    require_request_context,
    require_request_id,
    service_client,
    singleton_lifespan,
)
from .errors import (
    ServiceErrorContext,
    create_error_response,
    handle_service_error,
    service_error_handler,
)
from .responses import (
    ActionResponse,
    CollectionResponse,
    DetailResponse,
    ErrorResponse,
    PaginatedResponse,
    ResponseBuilder,
    SearchResponse,
)

__version__ = "0.2.0"

__all__ = [
    ***REMOVED*** Core app
    "create_app",
    "AppOptions",
    "FastAPIConfig",
    "FastAPIConfigMixin",
    ***REMOVED*** Service clients
    "ServiceClient",
    "ServiceConfig",
    ***REMOVED*** Error handling
    "handle_service_error",
    "create_error_response",
    "service_error_handler",
    "ServiceErrorContext",
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
    ***REMOVED*** Response utilities (NEW!)
    "ResponseBuilder",
    "PaginatedResponse",
    "DetailResponse",
    "CollectionResponse",
    "SearchResponse",
    "ActionResponse",
    "ErrorResponse",
    ***REMOVED*** Version
    "__version__",
]
