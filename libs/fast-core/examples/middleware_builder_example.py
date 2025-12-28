"""
Example: Using the Fast Core Middleware Builder

This example demonstrates how to use the new MiddlewareConfig system
for granular middleware configuration in FastAPI applications.
"""

import os

***REMOVED*** Import from the local fast_core package
import sys
from typing import Any, cast

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fast_core.app import create_app  ***REMOVED*** type: ignore
from fast_core.middleware import MiddlewareConfig  ***REMOVED*** type: ignore
from fastapi import APIRouter, FastAPI, Request


***REMOVED*** Example settings class
class Settings:
    service_name = "Example API"
    debug = True
    environment = "development"


settings = Settings()

***REMOVED*** Create routers for demonstration
api_router = APIRouter(prefix="/api/v1")


@api_router.get("/hello")
async def hello(request: Request) -> dict[str, Any]:
    """Example endpoint that shows middleware features."""
    return {
        "message": "Hello, World!",
        "request_id": getattr(request.state, "request_id", None),
        "headers": dict(request.headers),
    }


@api_router.get("/slow")
async def slow_endpoint() -> dict[str, str]:
    """Endpoint that takes time to demonstrate process time headers."""
    import asyncio

    await asyncio.sleep(1)
    return {"message": "This was slow"}


@api_router.post("/data")
async def post_data(data: dict) -> dict[str, Any]:
    """Endpoint for testing request body logging."""
    return {"received": data}


def create_basic_app() -> FastAPI:
    """Create an app with basic middleware configuration."""
    middleware = MiddlewareConfig()
    middleware.cors(
        origins=["http://localhost:3000", "https://app.example.com"], credentials=True
    ).request_processing(include_request_id=True, include_process_time=True)

    app = create_app(settings=settings, middleware=middleware, routers=[api_router])
    return cast(FastAPI, app)


def create_security_focused_app() -> FastAPI:
    """Create an app with security-focused middleware."""
    middleware = MiddlewareConfig()
    middleware.cors(
        origins=["https://secure-app.example.com"],
        credentials=True,
        methods=["GET", "POST", "PUT", "DELETE"],
    ).security_headers(
        hsts=True,
        hsts_max_age=31536000,  ***REMOVED*** 1 year
        frame_options="DENY",
        csp="default-src 'self'; script-src 'self' 'unsafe-inline'",
        trusted_hosts=["secure-app.example.com", "api.example.com"],
    ).rate_limiting(
        default_limit="100/minute",
        endpoints={
            "/api/v1/auth/login": "5/minute",
            "/api/v1/auth/register": "3/minute",
            "/api/v1/data": "50/minute",
        },
        exempt_ips=["127.0.0.1", "10.0.0.0/8"],
    )

    app = create_app(settings=settings, middleware=middleware, routers=[api_router])
    return cast(FastAPI, app)


def create_development_app() -> FastAPI:
    """Create an app with development-friendly middleware."""
    middleware = MiddlewareConfig()
    middleware.cors(origins=["*"], credentials=False).logging(  ***REMOVED*** Allow all origins in development
        level="DEBUG",
        include_request_body=True,
        include_response_body=True,
        max_body_size=2048,
        exclude_paths=["/health"],  ***REMOVED*** Don't log health checks
        log_timing=True,
        log_user_agent=True,
    ).request_processing(include_request_id=True, include_process_time=True, gzip_compression=True)

    app = create_app(settings=settings, middleware=middleware, routers=[api_router])
    return cast(FastAPI, app)


def create_production_app() -> FastAPI:
    """Create an app with production-ready middleware stack."""
    middleware = MiddlewareConfig()
    middleware.cors(
        origins=[
            "https://app.example.com",
            "https://mobile.example.com",
            "https://admin.example.com",
        ],
        credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        headers=["Content-Type", "Authorization", "X-Requested-With"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
    ).security_headers(
        hsts=True,
        hsts_max_age=63072000,  ***REMOVED*** 2 years
        hsts_include_subdomains=True,
        frame_options="DENY",
        content_type_options=True,
        xss_protection=True,
        csp="default-src 'self'; connect-src 'self' https://api.example.com",
        referrer_policy="strict-origin-when-cross-origin",
        trusted_hosts=["app.example.com", "api.example.com"],
    ).rate_limiting(
        default_limit="1000/hour",
        storage_url="redis://localhost:6379/0",  ***REMOVED*** Use Redis for distributed rate limiting
        endpoints={
            "/api/v1/auth/login": "10/minute",
            "/api/v1/auth/refresh": "20/minute",
            "/api/v1/upload": "5/minute",
            "/api/v1/search": "100/minute",
        },
        exempt_ips=["10.0.0.0/8", "192.168.0.0/16"],  ***REMOVED*** Internal networks
    ).logging(
        level="INFO",
        include_request_body=False,  ***REMOVED*** Don't log request bodies in production
        include_response_body=False,
        exclude_paths=["/health", "/metrics", "/favicon.ico"],
        include_headers=True,
        exclude_headers=["authorization", "cookie", "x-api-key"],
        log_timing=True,
        log_user_agent=False,  ***REMOVED*** Reduce log volume
    ).request_processing(
        max_request_size=5 * 1024 * 1024,  ***REMOVED*** 5MB max request size
        timeout=30,
        include_request_id=True,
        include_process_time=True,
        gzip_compression=True,
        gzip_minimum_size=1000,
    )

    app = create_app(settings=settings, middleware=middleware, routers=[api_router])
    return cast(FastAPI, app)


def create_minimal_app() -> FastAPI:
    """Create an app with minimal middleware (only what's needed)."""
    middleware = MiddlewareConfig()
    middleware.cors(origins=["http://localhost:3000"], credentials=False).request_processing(
        include_request_id=True,
        gzip_compression=False,  ***REMOVED*** Disable compression for minimal setup
    )

    app = create_app(settings=settings, middleware=middleware, routers=[api_router])
    return cast(FastAPI, app)


if __name__ == "__main__":
    import uvicorn

    ***REMOVED*** Choose which app configuration to run
    app_configs = {
        "basic": create_basic_app,
        "security": create_security_focused_app,
        "development": create_development_app,
        "production": create_production_app,
        "minimal": create_minimal_app,
    }

    ***REMOVED*** Default to basic configuration
    config_name = "basic"
    app = app_configs[config_name]()

    print(f"Starting {config_name} configuration...")
    print("Available endpoints:")
    print("  GET  /api/v1/hello")
    print("  GET  /api/v1/slow")
    print("  POST /api/v1/data")
    print("  GET  /docs (API documentation)")

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
