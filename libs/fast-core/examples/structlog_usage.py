"""
Example demonstrating structlog usage in Fast Core with best practices.

This example shows how to configure structlog for both development and production
environments with proper filtering and formatting.
"""

***REMOVED*** mypy: ignore-errors

import os
from typing import Any

import structlog
from fastapi import Request

***REMOVED*** Note: In a real application, these imports would work normally
***REMOVED*** These are example imports for demonstration purposes
try:
    from fast_core import AppOptions, create_app
    from fast_core.middleware import MiddlewareConfig
    from fast_core.middleware.logging import get_request_logger
except ImportError:
    ***REMOVED*** Fallback for when running in development/testing
    print("Note: This example requires fast_core to be properly installed")


def configure_structlog_for_environment(environment: str = "development") -> None:
    """Configure structlog based on environment."""

    if environment == "production":
        ***REMOVED*** Production: JSON logs for machine parsing
        processors: list[Any] = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ]
    else:
        ***REMOVED*** Development: Pretty console output
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,  ***REMOVED*** type: ignore[arg-type]
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


***REMOVED*** Configure based on environment
environment = os.getenv("ENVIRONMENT", "development")
configure_structlog_for_environment(environment)

logger = structlog.get_logger(__name__)


class ExampleSettings:
    """Example settings class."""

    service_name = "structlog-example"
    debug = environment == "development"
    host = "0.0.0.0"
    port = 8000


def create_example_app() -> Any:  ***REMOVED*** Using Any to avoid FastAPI import issues
    """Create example FastAPI app with improved structlog logging."""

    settings = ExampleSettings()

    ***REMOVED*** Configure middleware with improved logging settings
    try:
        middleware = MiddlewareConfig()
        middleware.logging(
            level="DEBUG" if settings.debug else "INFO",
            include_request_body=False,  ***REMOVED*** Usually disabled in production
            include_response_body=False,
            log_timing=True,
            include_headers=True,  ***REMOVED*** Now filtered to essential headers only
            exclude_paths=["/health", "/docs", "/openapi.json", "/metrics"],
            exclude_headers=["authorization", "cookie", "x-api-key"],  ***REMOVED*** Sensitive headers
        ).cors(origins=["*"] if settings.debug else ["https://yourdomain.com"], credentials=True)

        ***REMOVED*** Create app with middleware
        app = create_app(
            settings=settings,
            title="Structlog Best Practices API",
            description="Example API demonstrating structlog best practices",
            version="1.0.0",
            middleware=middleware,
            options=AppOptions(
                exception_handlers=True,
                health_checks=True,
                docs=settings.debug,  ***REMOVED*** Only enable docs in development
            ),
        )
    except NameError:
        ***REMOVED*** Fallback if fast_core is not available
        from fastapi import FastAPI

        app = FastAPI(title="Structlog Example (Fallback)")

    @app.get("/")  ***REMOVED*** type: ignore[misc]
    async def root() -> dict[str, Any]:
        """Root endpoint with structured logging."""
        logger.info("Root endpoint accessed", endpoint="/", action="get_root")
        return {"message": "Hello from structlog!", "environment": environment}

    @app.get("/api/users/{user_id}")  ***REMOVED*** type: ignore[misc]
    async def get_user(user_id: int, request: Request) -> dict[str, Any]:
        """Example endpoint demonstrating request-scoped logging with correlation."""
        ***REMOVED*** Get request-scoped logger with automatic request ID
        try:
            request_logger = get_request_logger(request)
        except NameError:
            request_logger = logger

        request_logger.info(
            "Processing user request",
            user_id=user_id,
            action="get_user",
            business_context="user_lookup",
        )

        if user_id < 1:
            request_logger.warning(
                "Invalid user ID provided",
                user_id=user_id,
                error_type="validation_error",
                action="get_user",
            )
            return {"error": "User ID must be positive", "code": "INVALID_USER_ID"}

        ***REMOVED*** Simulate some business logic
        user_data = {
            "user_id": user_id,
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com",
        }

        request_logger.info(
            "User request completed successfully",
            user_id=user_id,
            action="get_user",
            result="success",
        )

        return user_data

    @app.post("/api/users")  ***REMOVED*** type: ignore[misc]
    async def create_user(request: Request) -> dict[str, Any]:
        """Example endpoint showing structured logging for mutations."""
        try:
            request_logger = get_request_logger(request)
        except NameError:
            request_logger = logger

        request_logger.info(
            "User creation started", action="create_user", business_context="user_management"
        )

        ***REMOVED*** Simulate user creation
        new_user_id = 12345

        request_logger.info(
            "User created successfully",
            action="create_user",
            user_id=new_user_id,
            result="success",
            business_context="user_management",
        )

        return {"user_id": new_user_id, "status": "created"}

    @app.get("/api/error")  ***REMOVED*** type: ignore[misc]
    async def error_endpoint() -> dict[str, Any]:
        """Endpoint demonstrating error logging best practices."""
        try:
            ***REMOVED*** Simulate a business error
            raise ValueError("Database connection failed")
        except ValueError as e:
            logger.error(
                "Database error occurred",
                error_type="database_error",
                error_message=str(e),
                action="error_endpoint",
                severity="high",
                requires_investigation=True,
            )
            return {
                "error": "Internal server error",
                "code": "DATABASE_ERROR",
                "message": "Please try again later",
            }

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_example_app()

    logger.info(
        "Starting application",
        service="structlog-example",
        environment=environment,
        host="0.0.0.0",
        port=8000,
        debug=environment == "development",
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=None,  ***REMOVED*** Disable uvicorn's logging, use structlog
    )
