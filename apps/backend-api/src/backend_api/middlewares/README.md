***REMOVED*** Backend API Middlewares

The middlewares package contains custom FastAPI middlewares that handle cross-cutting concerns such as error handling, database monitoring, and request processing for the Next Watch Backend API service.

***REMOVED******REMOVED*** Architecture Overview

The middlewares follow the FastAPI/Starlette middleware pattern and are configured in the core application setup:

```text
middlewares/
├── __init__.py                  ***REMOVED*** Package exports
├── error_handler.py            ***REMOVED*** Global error handling middleware
├── database_monitoring.py      ***REMOVED*** Database query monitoring
└── README.md                   ***REMOVED*** This documentation
```

***REMOVED******REMOVED*** Middleware Components

***REMOVED******REMOVED******REMOVED*** Error Handler Middleware (`error_handler.py`)

Provides centralized exception handling with standardized error responses and comprehensive logging.

***REMOVED******REMOVED******REMOVED******REMOVED*** Features

- **Service Error Mapping**: Converts custom service exceptions to appropriate HTTP responses
- **Structured Logging**: Logs errors with detailed context including request path and error details
- **Debug Support**: Includes error details in development mode via query parameter
- **Standardized Responses**: Consistent JSON error response format

***REMOVED******REMOVED******REMOVED******REMOVED*** Supported Error Types

- `ValidationError` → HTTP 400 Bad Request
- `ResourceNotFoundError` → HTTP 404 Not Found
- `ConflictError` → HTTP 409 Conflict
- `PermissionError` → HTTP 403 Forbidden
- `ServiceError` → Mapped via `service_error_to_http_exception()`
- Generic exceptions → HTTP 500 Internal Server Error

***REMOVED******REMOVED******REMOVED******REMOVED*** Usage

```python
from backend_api.middlewares import ErrorHandlerMiddleware

app.add_middleware(ErrorHandlerMiddleware)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Error Response Format

```json
{
  "message": "Resource not found",
  "details": {
    "resource_type": "movie",
    "resource_id": "123"
  }
}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Debug Mode

Add `?debug=1` to any request to include error details in development:

```json
{
  "message": "An unexpected error occurred",
  "details": {
    "error": "Database connection failed"
  }
}
```

***REMOVED******REMOVED******REMOVED*** Database Monitoring Middleware (`database_monitoring.py`)

Tracks database queries per request with performance monitoring and structured logging.

***REMOVED******REMOVED******REMOVED******REMOVED*** Features

- **Query Counting**: Tracks number of database queries per request
- **Performance Monitoring**: Measures total request duration
- **Request Context**: Maintains request-scoped context with user information
- **Debug Headers**: Adds debugging headers in development mode
- **Structured Logging**: Logs request summaries with database statistics
- **Slow Query Detection**: Identifies and logs slow requests and high query counts

***REMOVED******REMOVED******REMOVED******REMOVED*** Configuration

```python
from backend_api.middlewares.database_monitoring import DatabaseMonitoringMiddleware

app.add_middleware(
    DatabaseMonitoringMiddleware,
    log_all_requests=True  ***REMOVED*** Set to False to only log requests with queries
)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Debug Headers (Development Mode)

- `X-DB-Query-Count`: Number of database queries executed
- `X-Request-Duration-Ms`: Total request duration in milliseconds
- `X-Request-ID`: Unique request identifier

***REMOVED******REMOVED******REMOVED******REMOVED*** Request Context

The middleware maintains request-scoped context:

```python
from backend_api.core.request_context import get_request_context

context = get_request_context()
print(f"Query count: {context.query_count}")
print(f"Request ID: {context.request_id}")
print(f"User ID: {context.user_id}")
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Performance Thresholds

- **Slow Requests**: > 2000ms total duration
- **High Query Count**: > 10 database queries
- **Error Responses**: HTTP status >= 400

***REMOVED******REMOVED******REMOVED******REMOVED*** Log Levels

- `INFO`: Normal requests with database activity
- `WARNING`: Slow requests, high query counts, or error responses
- `ERROR`: Unhandled exceptions during request processing

***REMOVED******REMOVED*** Configuration

Middlewares are configured in `src/backend_api/core/middleware.py`:

```python
def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the FastAPI application."""

    ***REMOVED*** CORS middleware (configured first)
    app.add_middleware(CORSMiddleware, ...)

    ***REMOVED*** Error handling middleware
    app.add_middleware(ErrorHandlerMiddleware)

    ***REMOVED*** Database monitoring middleware (if enabled)
    if settings.database_monitoring_enabled:
        app.add_middleware(
            DatabaseMonitoringMiddleware,
            log_all_requests=settings.debug
        )

    ***REMOVED*** Performance metrics middleware (if enabled)
    if settings.enable_performance_metrics:
        setup_performance_middleware(app)
```

***REMOVED******REMOVED******REMOVED*** Configuration Options

Settings from `backend_api.config.app.settings`:

- `database_monitoring_enabled`: Enable/disable database monitoring middleware
- `debug`: Debug mode affects logging verbosity and header inclusion
- `enable_performance_metrics`: Enable performance timing headers

***REMOVED******REMOVED*** Integration with Other Components

***REMOVED******REMOVED******REMOVED*** Error Handling Integration

```python
from backend_api.errors import ResourceNotFoundError

***REMOVED*** Service layer
async def get_movie(movie_id: int):
    movie = await db.get_movie(movie_id)
    if not movie:
        raise ResourceNotFoundError(
            message="Movie not found",
            details={"movie_id": movie_id}
        )
    return movie

***REMOVED*** Middleware automatically handles the exception
***REMOVED*** Returns: HTTP 404 with standardized JSON response
```

***REMOVED******REMOVED******REMOVED*** Request Context Integration

```python
from backend_api.core.request_context import get_request_context

async def some_database_operation():
    context = get_request_context()
    logger.info(
        "Executing database operation",
        request_id=context.request_id,
        user_id=context.user_id
    )
    ***REMOVED*** Database query is automatically counted
    result = await db.execute(query)
    return result
```

***REMOVED******REMOVED******REMOVED*** Logging Integration

All middlewares use the shared logging configuration:

```python
from config.logging import get_logger

logger = get_logger(__name__)  ***REMOVED*** Creates "backend_api.middlewares.error_handler"
```

***REMOVED******REMOVED*** Usage Examples

***REMOVED******REMOVED******REMOVED*** Basic Setup

```python
from fastapi import FastAPI
from backend_api.middlewares import ErrorHandlerMiddleware
from backend_api.middlewares.database_monitoring import DatabaseMonitoringMiddleware

app = FastAPI()

***REMOVED*** Add middlewares in correct order
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(DatabaseMonitoringMiddleware, log_all_requests=True)
```

***REMOVED******REMOVED******REMOVED*** Custom Error Handling

```python
from backend_api.errors import ServiceError

class CustomBusinessError(ServiceError):
    """Custom business logic error."""
    pass

***REMOVED*** The ErrorHandlerMiddleware will automatically handle this
***REMOVED*** and convert it to an appropriate HTTP response
async def business_operation():
    if condition_failed:
        raise CustomBusinessError(
            message="Business rule violation",
            details={"rule": "minimum_age", "provided": 16, "required": 18}
        )
```

***REMOVED******REMOVED******REMOVED*** Request Context Usage

```python
from backend_api.core.request_context import get_request_context

async def audit_log_operation(action: str):
    context = get_request_context()

    audit_entry = AuditLog(
        request_id=context.request_id,
        user_id=context.user_id,
        action=action,
        timestamp=context.start_time
    )
    await db.save(audit_entry)
```

***REMOVED******REMOVED*** Performance Monitoring

***REMOVED******REMOVED******REMOVED*** Query Performance Tracking

```python
***REMOVED*** Example log output for a slow request:
{
    "level": "WARNING",
    "message": "Slow request detected",
    "request_id": "req_123456",
    "method": "GET",
    "path": "/api/v1/movies",
    "user_id": "user_789",
    "status_code": 200,
    "total_duration_ms": 2500.75,
    "db_query_count": 12,
    "slow_request": true
}
```

***REMOVED******REMOVED******REMOVED*** Development Headers

```http
GET /api/v1/movies/123
X-DB-Query-Count: 3
X-Request-Duration-Ms: 45.23
X-Request-ID: req_123456
```

***REMOVED******REMOVED*** Testing

***REMOVED******REMOVED******REMOVED*** Unit Testing

```python
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from backend_api.middlewares import ErrorHandlerMiddleware
from backend_api.errors import ResourceNotFoundError

def test_error_handler_middleware():
    app = FastAPI()
    app.add_middleware(ErrorHandlerMiddleware)

    @app.get("/test")
    async def test_endpoint():
        raise ResourceNotFoundError("Test error")

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 404
    assert "Test error" in response.json()["message"]
```

***REMOVED******REMOVED******REMOVED*** Integration Testing

```python
@pytest.mark.asyncio
async def test_database_monitoring():
    app = create_test_app()
    app.add_middleware(DatabaseMonitoringMiddleware, log_all_requests=True)

    with TestClient(app) as client:
        response = client.get("/api/v1/movies")

        ***REMOVED*** Check debug headers are present in test mode
        assert "X-DB-Query-Count" in response.headers
        assert "X-Request-Duration-Ms" in response.headers
```

***REMOVED******REMOVED*** Best Practices

***REMOVED******REMOVED******REMOVED*** Error Handling

1. **Use Specific Exceptions**: Create specific exception types for different error conditions
2. **Include Context**: Always include relevant details in error messages
3. **Log Appropriately**: Log errors with sufficient context for debugging
4. **User-Friendly Messages**: Provide clear, actionable error messages

***REMOVED******REMOVED******REMOVED*** Performance Monitoring

1. **Set Thresholds**: Configure appropriate thresholds for slow requests
2. **Monitor Query Counts**: Watch for N+1 query problems
3. **Use Structured Logging**: Include relevant context in log entries
4. **Enable Debug Headers**: Use debug headers for development troubleshooting

***REMOVED******REMOVED******REMOVED*** Request Context

1. **Clean Up**: Always clear context after request completion
2. **Extract User Info**: Implement proper user identification for audit trails
3. **Thread Safety**: Be aware of async context in concurrent requests

***REMOVED******REMOVED*** Future Enhancements

***REMOVED******REMOVED******REMOVED*** Planned Features

1. **Rate Limiting**: Request rate limiting middleware
2. **Circuit Breaker**: Circuit breaker for external service calls
3. **Metrics Collection**: Prometheus metrics integration
4. **Request Tracing**: OpenTelemetry distributed tracing
5. **Security Headers**: Security-focused middleware (HSTS, CSP, etc.)

***REMOVED******REMOVED******REMOVED*** Performance Improvements

1. **Async Context**: Enhanced async context management
2. **Memory Optimization**: Reduce memory overhead of request tracking
3. **Batch Logging**: Batch log entries for high-traffic scenarios
4. **Custom Metrics**: More granular performance metrics

***REMOVED******REMOVED*** Dependencies

***REMOVED******REMOVED******REMOVED*** Required

- `fastapi`: Web framework and middleware base classes
- `starlette`: Base middleware functionality
- `config @ file:../../libs/config`: Shared logging configuration

***REMOVED******REMOVED******REMOVED*** Internal Dependencies

- `backend_api.errors`: Custom exception definitions
- `backend_api.core.request_context`: Request-scoped context management
- `backend_api.config.app`: Application configuration

The middlewares package provides essential cross-cutting functionality that ensures consistent error handling, performance monitoring, and request processing across the entire Backend API service.
