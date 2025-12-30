# BFF Core Module

The core module contains the foundational components of the Next Watch BFF (Backend for Frontend) service, now **fully integrated with fast-core** for standardized FastAPI application patterns.

## Overview

The BFF service acts as an aggregation layer between frontend applications and backend microservices, providing:

- **Data Aggregation**: Combines data from multiple backend services
- **Request/Response Transformation**: Formats data for frontend consumption
- **Authentication Proxy**: Handles user authentication and authorization
- **Caching Layer**: Optimizes performance through intelligent caching
- **Error Handling**: Provides consistent error responses
- **API Versioning**: Supports multiple API versions for frontend compatibility

## Fast-Core Integration Architecture

The core module now leverages **fast-core** for standardized application patterns:

```
bff_api/core/
├── __init__.py              # Module exports (fast-core integration)
├── app_fast_core.py         # Fast-core application factory
└── README.md               # This documentation
```

**Removed Files** (replaced by fast-core):

- ~~`app.py`~~ → `app_fast_core.py` (fast-core integration)
- ~~`middleware.py`~~ → fast-core middleware system
- ~~`logging.py`~~ → fast-core logging configuration

## Components

### Fast-Core Application Factory (`app_fast_core.py`)

The application factory now uses fast-core's standardized patterns:

#### **Application Creation**

```python
from bff_api.core import create_app

app = create_app()  # Uses fast-core internally
```

#### **Fast-Core Integration**

- **Configuration Adapter**: Converts `BFFAPIConfig` to fast-core's `FastAPIConfig`
- **Service Dependencies**: Pre-configured HTTP clients for all backend services
- **Middleware Stack**: Automatic logging, CORS, security, and error handling
- **Health Checks**: Comprehensive monitoring of external dependencies

#### **Service Client Dependencies**

Fast-core provides dependency injection for service clients:

```python
from fast_core.dependencies import get_backend_client, get_auth_client
from fastapi import Depends

async def get_movies(
    backend = Depends(get_backend_client),
    auth = Depends(get_auth_client),
):
    # Use pre-configured httpx.AsyncClient instances
    movies = await backend.get("/movies")
    user = await auth.get("/user/profile")
    return {"movies": movies, "user": user}
```

#### **Lifespan Management**

- **Startup**: Logs configuration, tests service connections
- **Shutdown**: Closes singleton `BackendClient` and cleans up resources
- **Error Handling**: Graceful handling of startup/shutdown failures

### Fast-Core Middleware (Automatic)

Fast-core automatically configures all middleware:

#### **Logging Middleware**

- Request/response logging with request IDs
- Configurable exclusion paths (`/health`, `/docs`)
- Performance timing and structured logging

#### **CORS Middleware**

- Configured from `CORS_ORIGINS` environment variable
- Supports credentials and custom headers
- Production-safe origin restrictions

#### **Security Middleware**

- Trusted host validation in production
- Security headers and request validation
- Rate limiting capabilities

#### **Error Handling**

- Global exception handlers
- Consistent error response format
- Detailed logging for debugging

### Fast-Core Dependencies

Service clients are automatically configured and injected:

```python
# Available dependencies
from fast_core.dependencies import (
    get_backend_client,        # Main backend API
    get_auth_client,          # Authentication service
    get_recommendation_client, # Recommendation service
    get_ml_client,            # Machine learning service
)
```

## Architecture Changes

### What Fast-Core Provides

✅ **Application Factory**: Standardized FastAPI app creation
✅ **Middleware Stack**: Logging, CORS, security, error handling
✅ **Service Dependencies**: Pre-configured HTTP clients
✅ **Health Monitoring**: Comprehensive health check system
✅ **Configuration**: Enhanced configuration with service URLs and features
✅ **Exception Handling**: Global error handling and logging

### What BFF Still Manages

✅ **Business Logic**: Route handlers and data aggregation
✅ **BFF Configuration**: Service-specific settings (`BFFAPIConfig`)
✅ **Cache Integration**: BFF-specific caching patterns
✅ **Service Facades**: `BackendClient` facade for cache compatibility
✅ **Route Organization**: BFF-specific route structure

### Migration Benefits

1. **Reduced Boilerplate**: Eliminated 200+ lines of custom middleware code
2. **Enhanced Features**: Better logging, health checks, error handling
3. **Standardization**: Consistent patterns across all services
4. **Type Safety**: Improved dependency injection and configuration
5. **Maintainability**: Single source of truth for common functionality

## Lifecycle Management

### Startup Sequence

1. **Configuration Loading**: `BFFAPIConfig` loads environment variables
2. **Fast-Core Adapter**: Converts to `FastAPIConfig` with service URLs and features
3. **App Creation**: Fast-core creates FastAPI app with all middleware
4. **Dependency Registration**: Service clients configured and registered
5. **Route Registration**: BFF routes registered with dependency injection
6. **Health Initialization**: External service monitoring started

### Shutdown Sequence

1. **Singleton Cleanup**: Close shared `BackendClient` instance
2. **Fast-Core Cleanup**: Automatic cleanup of fast-core resources
3. **Resource Cleanup**: Close any remaining connections

## Service Integration

### Backend Client Integration (Enhanced)

The BFF uses a singleton `BackendClient` for optimal performance:

```python
# In route handlers
from bff_api.dependencies.backend import get_backend_client
from fastapi import Depends

async def get_movies(
    backend: BackendClient = Depends(get_backend_client),
):
    # Uses singleton instance with cache compatibility
    movies = await backend.get_movies()
    return movies
```

### Service Client Dependencies

Fast-core provides HTTP clients for all services:

```python
from fast_core.dependencies import get_ml_client
from fastapi import Depends

async def get_recommendations(
    ml_client = Depends(get_ml_client),
):
    # Direct HTTP client for services without facades
    response = await ml_client.get("/recommendations")
    return response.json()
```

### Health Monitoring

Fast-core automatically provides health endpoints:

- `/health` - Overall service health
- `/health/ready` - Readiness probe
- `/health/live` - Liveness probe

## Configuration

The core module uses the fast-core configuration adapter:

```python
# BFF-specific configuration (still used)
from bff_api.config.app import BFFAPIConfig

settings = BFFAPIConfig()

# Fast-core configuration (automatic)
from bff_api.config.fast_core_config import create_fast_core_config

fast_core_config = create_fast_core_config(settings)
```

### Service URLs

```bash
# All service endpoints configured via environment
BACKEND_API_URL=http://localhost:8000
AUTH_API_URL=http://localhost:8002
RECOMMENDATION_API_URL=http://localhost:8003
ML_API_URL=http://localhost:8004
```

### Feature Flags

```bash
# Control feature availability
ENABLE_RECOMMENDATIONS=true
ENABLE_ML_FEATURES=false
ENABLE_AUTH_SERVICE=true
```

## Error Handling

### Fast-Core Global Handlers

All exceptions are automatically handled by fast-core:

- **HTTP Exceptions**: Proper status codes and error messages
- **Validation Errors**: Detailed field-level error information
- **Unhandled Exceptions**: Logged and converted to 500 responses

### Service-Level Error Handling

Individual routes handle service-specific errors:

```python
from bff_api.routes.v1.movies import _handle_backend_error

async def get_movie_details(movie_id: int, backend = Depends(get_backend_client)):
    try:
        movie = await backend.get_movie(movie_id)
        return movie
    except Exception as e:
        await _handle_backend_error(e, "get_movie_details")
```

## Testing

### Fast-Core Integration Testing

```python
from bff_api.core import create_app

def test_app_creation():
    app = create_app()
    assert app.title == "BFF API"
    assert app.version == "1.0.0"

    # Fast-core features enabled
    assert hasattr(app.state, 'settings')
```

### Service Client Testing

```python
from fast_core.dependencies import get_backend_client

@pytest.mark.asyncio
async def test_service_dependencies():
    # Test dependency injection
    backend = await get_backend_client()
    assert backend is not None
```

## Best Practices

### Development

1. **Use Fast-Core Dependencies**: Import from `fast_core.dependencies`
2. **BFF Configuration**: Continue using `BFFAPIConfig` for BFF-specific settings
3. **Service Facades**: Use `BackendClient` facade for cache compatibility
4. **Error Handling**: Leverage fast-core's global error handling

### Production

1. **Configuration**:

   - Set specific service URLs (no localhost)
   - Configure proper timeouts per service
   - Enable appropriate feature flags

2. **Monitoring**:

   - Use fast-core health endpoints for load balancer checks
   - Monitor service client error rates
   - Track cache hit/miss ratios

3. **Security**:
   - Configure CORS origins properly
   - Use HTTPS for all service URLs
   - Set appropriate timeout values

## Migration Guide

### Old Pattern (Removed)

```python
# OLD: Manual setup (no longer available)
from bff_api.core.app import create_app
from bff_api.middlewares import LoggingMiddleware, AuthMiddleware

app = create_app()
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)
```

### New Pattern (Current)

```python
# NEW: Fast-core integration
from bff_api.core import create_app

# Everything configured automatically
app = create_app()
```

### Dependency Updates

```python
# OLD: Manual client instantiation
from bff_api.services.clients import BackendClient
backend_client = BackendClient(config)

# NEW: Dependency injection
from fast_core.dependencies import get_backend_client
from fastapi import Depends

async def route(backend = Depends(get_backend_client)):
    pass
```

## Future Enhancements

1. **Enhanced Monitoring**: Metrics collection and distributed tracing
2. **Circuit Breakers**: Automatic failure handling for external services
3. **Request Caching**: Intelligent response caching at the middleware level
4. **Rate Limiting**: Per-client rate limiting capabilities
5. **Service Mesh**: Integration with service mesh technologies

---

This core module now provides a robust, standardized foundation built on fast-core, maintaining BFF-specific functionality while leveraging shared infrastructure patterns across the entire platform.
