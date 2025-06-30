"""Fast-Core application factory for Search API.

This module creates a FastAPI application using the fast-core library
with Search-specific configuration and dependencies.
"""

from typing import List, Optional, AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fast_core import create_app, AppOptions
from fast_core.middleware import MiddlewareConfig

from search_api.config.app import SearchAPIConfig
from search_api.config.fast_core_config import create_fast_core_config
from search_api.dependencies.clients import cleanup_service_clients, get_all_services_health
from config.logging import get_logger

***REMOVED*** Import Search routes
from search_api.routes.health import router as health_router
from search_api.routes.meta import router as meta_router
from search_api.routes.api_v1 import api_v1_router

logger = get_logger(__name__)


@asynccontextmanager
async def search_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for Search API.

    Handles startup and shutdown events for the Search API application.
    Now uses Service Client Factory for better lifecycle management.
    """
    ***REMOVED*** Startup
    logger.info("Starting Search API application with Service Client Factory")
    settings = app.state.settings
    search_config = app.state.search_config

    ***REMOVED*** Log configuration summary
    logger.info(f"Search API starting on {settings.host}:{settings.port}")
    logger.info(f"Environment: {settings.environment}")

    ***REMOVED*** Initialize Search-specific metrics (always enabled for observability)
    try:
        from search_api.core.metrics import initialize_search_metrics

        metrics_instance = initialize_search_metrics()
        if metrics_instance:
            logger.info("Search metrics initialized successfully")
            app.state.metrics = metrics_instance
        else:
            logger.warning(
                "Search metrics initialization returned None - metrics registry not available"
            )
    except ImportError as e:
        logger.error(f"Failed to import Search metrics module: {e}")
    except Exception as e:
        logger.error(f"Error initializing Search metrics: {e}")

    ***REMOVED*** Initialize search-specific services
    suggestion_engine = None
    try:
        ***REMOVED*** Initialize Redis connection for suggestions
        logger.info("Initializing Redis connection for search suggestions")
        from search_api.services.suggestion_engine import SuggestionEngine

        ***REMOVED*** Create global suggestion engine instance
        suggestion_engine = SuggestionEngine(
            redis_url=search_config.redis_url,
            max_connections=search_config.redis_max_connections,
            suggestion_key_prefix=search_config.redis_suggestion_key_prefix,
            entity_key_prefix=search_config.redis_entity_key_prefix,
            search_result_prefix=search_config.redis_search_result_prefix,
        )
        await suggestion_engine.initialize()

        ***REMOVED*** Store in app state for access by routes
        app.state.suggestion_engine = suggestion_engine
        logger.info("Suggestion engine initialized successfully")

        ***REMOVED*** Initialize search analytics if enabled
        if search_config.enable_search_analytics:
            logger.info("Search analytics enabled")
            ***REMOVED*** TODO: Initialize analytics service here when implemented
            ***REMOVED*** analytics_service = AnalyticsService(config=search_config)
            ***REMOVED*** await analytics_service.initialize()
            ***REMOVED*** app.state.analytics_service = analytics_service
            ***REMOVED*** logger.info("Analytics service initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing search services: {e}")
        ***REMOVED*** Clean up partially initialized services
        if suggestion_engine:
            try:
                await suggestion_engine.shutdown()
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up suggestion engine: {cleanup_error}")
        raise

    ***REMOVED*** Test service connections on startup
    if settings.debug:
        logger.debug("Testing service connections with Service Client Factory...")
        try:
            ***REMOVED*** Get health status for all registered services
            health_status = await get_all_services_health()
            for service_name, status in health_status.items():
                if status.get("status") == "healthy":
                    logger.debug(f"✓ {service_name}: {status.get('url')} - healthy")
                else:
                    logger.warning(
                        f"⚠ {service_name}: {status.get('url')} - {status.get('status')}"
                    )
        except Exception as e:
            logger.warning(f"Could not test service connections during startup: {e}")

    yield

    ***REMOVED*** Shutdown
    logger.info("Shutting down Search API application")

    ***REMOVED*** Clean up search-specific services
    try:
        ***REMOVED*** Close suggestion engine connections
        if hasattr(app.state, "suggestion_engine") and app.state.suggestion_engine:
            logger.info("Shutting down suggestion engine")
            await app.state.suggestion_engine.shutdown()
            app.state.suggestion_engine = None
            logger.info("Suggestion engine shut down successfully")

        ***REMOVED*** Close analytics connections
        if hasattr(app.state, "analytics_service") and app.state.analytics_service:
            logger.info("Shutting down analytics service")
            ***REMOVED*** TODO: Implement analytics service shutdown when available
            ***REMOVED*** await app.state.analytics_service.shutdown()
            ***REMOVED*** app.state.analytics_service = None
            logger.info("Analytics service shut down successfully")

        logger.info("Search services cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during search services cleanup: {e}")

    ***REMOVED*** Clean up all service clients managed by Service Client Factory
    try:
        await cleanup_service_clients()
        logger.info("All service clients cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during service client cleanup: {e}")


def create_search_middleware_config(config: SearchAPIConfig) -> MiddlewareConfig:
    """Create Search-specific middleware configuration using the Middleware Builder.

    Args:
        config: Search API configuration

    Returns:
        Configured middleware with Search-specific settings
    """
    middleware = MiddlewareConfig()

    ***REMOVED*** Configure CORS for Search API
    middleware.cors(
        origins=config.cors_origins,
        credentials=True,
        methods=["GET", "POST", "OPTIONS"],  ***REMOVED*** Search is primarily GET-based
        headers=["Content-Type", "Authorization", "X-Requested-With", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-Process-Time", "X-Cache-Status"],
        max_age=3600,  ***REMOVED*** Cache preflight requests for 1 hour
    )

    ***REMOVED*** Configure security headers for production
    if config.is_production:
        middleware.security_headers(
            hsts=True,
            hsts_max_age=63072000,  ***REMOVED*** 2 years
            hsts_include_subdomains=True,
            frame_options="DENY",  ***REMOVED*** Prevent iframe embedding
            content_type_options=True,
            xss_protection=True,
            csp="default-src 'self'; connect-src 'self' https://*.example.com; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'",
            referrer_policy="strict-origin-when-cross-origin",
            trusted_hosts=config.allowed_hosts,
        )
    else:
        ***REMOVED*** Development security headers (more permissive)
        middleware.security_headers(
            hsts=False,  ***REMOVED*** No HSTS in development
            frame_options="SAMEORIGIN",
            content_type_options=True,
            xss_protection=True,
            referrer_policy="strict-origin-when-cross-origin",
        )

    ***REMOVED*** Configure rate limiting for Search API protection
    rate_limit_config = {
        ***REMOVED*** Search endpoints (higher limits for good UX)
        "/api/v1/search": "100/minute",
        "/api/v1/search/suggestions": "200/minute",  ***REMOVED*** Higher for typeahead
        "/api/v1/search/suggestions/text": "200/minute",
        "/api/v1/search/all": "50/minute",
        ***REMOVED*** Health and meta endpoints (less restrictive)
        "/health": "1000/minute",
        "/meta": "1000/minute",
    }

    middleware.rate_limiting(
        default_limit="300/hour" if config.is_production else "1000/hour",
        endpoints=rate_limit_config,
        exempt_ips=["127.0.0.1", "::1"]
        + (["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"] if not config.is_production else []),
        headers=True,  ***REMOVED*** Include rate limit headers for debugging
        key_func="ip",  ***REMOVED*** Rate limit by IP address
    )

    ***REMOVED*** Configure logging for Search API
    log_level = "INFO" if config.is_production else "DEBUG"
    middleware.logging(
        level=log_level,
        include_request_body=not config.is_production,  ***REMOVED*** Only log bodies in development
        include_response_body=False,  ***REMOVED*** Never log response bodies (too verbose)
        max_body_size=1024,  ***REMOVED*** Smaller for search queries
        exclude_paths=["/health", "/docs", "/openapi.json", "/favicon.ico"],
        include_headers=True,
        exclude_headers=["authorization", "cookie", "x-api-key", "internal-api-key"],
        log_timing=True,
        log_user_agent=not config.is_production,  ***REMOVED*** Only in development
    )

    ***REMOVED*** Configure request processing for Search API
    middleware.request_processing(
        max_request_size=1 * 1024 * 1024,  ***REMOVED*** 1MB for search requests
        timeout=config.search_timeout_seconds,  ***REMOVED*** Use search-specific timeout
        include_request_id=True,
        request_id_header="X-Request-ID",
        include_process_time=True,
        process_time_header="X-Process-Time",
        gzip_compression=True,
        gzip_minimum_size=500,  ***REMOVED*** Smaller threshold for search responses
    )

    ***REMOVED*** Configure metrics middleware for Search API monitoring
    middleware.metrics(
        endpoint_path="/metrics",
        include_endpoint=True,
        exclude_paths=["/health", "/metrics", "/docs", "/openapi.json", "/favicon.ico"],
        exclude_methods=["OPTIONS"],
        custom_buckets=[
            0.005,
            0.01,
            0.025,
            0.05,
            0.075,
            0.1,
            0.25,
            0.5,
            0.75,
            1.0,
            2.5,
            5.0,
            7.5,
            10.0,
        ],
        track_request_size=True,
        track_response_size=True,
        enabled=True,  ***REMOVED*** Always enable metrics for production observability
    )
    logger.info("Metrics middleware enabled for Search API monitoring")

    logger.info(f"Search middleware configured for {config.environment} environment")
    return middleware


def create_search_app(config: Optional[SearchAPIConfig] = None) -> FastAPI:
    """Create Search API application using fast-core with enhanced middleware.

    Args:
        config: Search API configuration (creates default if None)

    Returns:
        Configured FastAPI application
    """
    ***REMOVED*** Create or use provided configuration
    if config is None:
        config = SearchAPIConfig()

    logger.info("Creating Search API application with fast-core and enhanced middleware")

    ***REMOVED*** Convert Search config to fast-core config
    fast_core_config = create_fast_core_config(config)

    ***REMOVED*** Create Search-specific middleware configuration
    middleware_config = create_search_middleware_config(config)

    ***REMOVED*** Define routers for the application
    routers = [
        meta_router,
        health_router,
        api_v1_router,
    ]

    ***REMOVED*** Create FastAPI application using fast-core
    app = create_app(
        settings=fast_core_config,
        title="Next Watch Search API",
        description="Search and suggestion service for Next Watch platform",
        version="0.1.0",
        options=AppOptions(
            exception_handlers=True,
            health_checks=True,
            docs=not config.is_production,  ***REMOVED*** Disable docs in production
        ),
        middleware=middleware_config,
        routers=routers,
        lifespan=search_lifespan,
    )

    ***REMOVED*** Store the original SearchAPIConfig in app state for access to search-specific settings
    app.state.search_config = config

    logger.info("Search API application created successfully with fast-core")
    return app


def get_search_app() -> FastAPI:
    """Get or create Search API application instance.

    Returns:
        FastAPI application instance
    """
    return create_search_app()
