# Core Module

This module contains the core application components that handle FastAPI application creation, configuration, and lifecycle management using the Application Factory pattern.

## Overview

The core module provides:

- **Application Factory**: Clean app creation with dependency injection
- **Middleware Configuration**: CORS, security, and other middleware setup
- **Logging Configuration**: Centralized logging setup with external library suppression
- **Lifecycle Management**: Proper startup and shutdown handling
- **Exception Handling**: Global exception handling for unhandled errors

## Architecture

The core module follows the Application Factory pattern, separating concerns into focused modules:

```
core/
├── __init__.py         # Module exports
├── app.py              # FastAPI app factory & lifespan management
├── middleware.py       # Middleware configuration (CORS, TrustedHost)
└── logging.py          # Logging setup wrapper
```

## Components

### Application Factory (`app.py`)

The main application factory that creates and configures the FastAPI application:

```python
from recommendation_api.core.app import create_app

# Create a configured FastAPI application
app = create_app()
```

**Features:**

- **Lifespan Management**: Handles startup/shutdown with proper resource cleanup
- **Service Initialization**: Sets up health service and other dependencies
- **Router Integration**: Includes all route modules with proper tagging
- **Exception Handling**: Global exception handler for unhandled errors
- **Configuration**: Uses settings for debug mode, title, description

**Lifespan Events:**

- **Startup**: Initialize health service, log configuration
- **Shutdown**: Clean up health service and other resources

### Middleware Configuration (`middleware.py`)

Configures FastAPI middleware for security and cross-origin requests:

```python
from recommendation_api.core.middleware import setup_middleware

# Setup middleware on an existing app
setup_middleware(app)
```

**Middleware Included:**

- **CORS Middleware**: Cross-origin request handling
- **TrustedHost Middleware**: Host validation in production
- **Future**: Rate limiting, authentication, request logging

**Configuration:**

- Development: Permissive CORS for local development
- Production: Restricted hosts and origins based on settings

### Logging Configuration (`logging.py`)

Provides a simple interface to the comprehensive logging system:

```python
from recommendation_api.core.logging import setup_logging

# Configure application logging
setup_logging()
```

**Features:**

- **Settings Integration**: Uses application settings for log level
- **Comprehensive Config**: Delegates to `config.logging` for full features
- **Environment Aware**: Adjusts verbosity based on debug mode
- **External Library Suppression**: Reduces noise from third-party libraries

## Usage

### Basic Application Creation

```python
from recommendation_api.core import create_app

# Create the application
app = create_app()

# The app is fully configured and ready to run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Custom Configuration

```python
from recommendation_api.core.app import create_app
from recommendation_api.core.middleware import setup_middleware

# Create base app
app = create_app()

# Add custom middleware
@app.middleware("http")
async def custom_middleware(request, call_next):
    # Custom logic here
    response = await call_next(request)
    return response
```

### Testing Setup

```python
from fastapi.testclient import TestClient
from recommendation_api.core import create_app

def test_app():
    app = create_app()
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
```

## Application Lifecycle

### Startup Sequence

1. **Environment Loading**: Load environment variables and settings
2. **Logging Setup**: Configure logging with appropriate levels
3. **App Creation**: Create FastAPI instance with metadata
4. **Middleware Setup**: Configure CORS, security middleware
5. **Router Registration**: Include all route modules
6. **Service Initialization**: Initialize health service and dependencies
7. **Exception Handlers**: Register global exception handlers

### Shutdown Sequence

1. **Service Cleanup**: Close health service connections
2. **Resource Cleanup**: Clean up any other resources
3. **Logging**: Log shutdown completion

## Health Service Integration

The core module manages the health service lifecycle:

```python
# During startup
app.state.health_service = get_health_service()

# During shutdown
if hasattr(app.state, 'health_service') and app.state.health_service:
    app.state.health_service.close()
```

**Benefits:**

- **Single Instance**: One health service instance per application
- **Proper Cleanup**: Connections are closed on shutdown
- **State Management**: Stored in app.state for route access

## Exception Handling

Global exception handler for unhandled errors:

```python
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

**Features:**

- **Logging**: All unhandled exceptions are logged with stack traces
- **Consistent Response**: Returns structured error response
- **Security**: Doesn't expose internal error details to clients

## Configuration Integration

The core module integrates with the application settings:

```python
from recommendation_api.config import settings

# App metadata from settings
app = FastAPI(
    title="Recommendation API",
    description="AI-powered movie recommendation service",
    version="0.1.0",
    debug=settings.debug,
)

# Middleware configuration
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )
```

## Best Practices

### Application Factory Pattern

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Injection**: Dependencies are injected, not created internally
3. **Configuration**: Use settings for all configurable values
4. **Testing**: Factory pattern makes testing easier with different configurations

### Resource Management

1. **Lifespan Events**: Use lifespan for proper startup/shutdown
2. **State Management**: Store shared resources in app.state
3. **Cleanup**: Always clean up resources in shutdown handler
4. **Error Handling**: Handle initialization errors gracefully

### Development vs Production

1. **Debug Mode**: Different behavior based on settings.debug
2. **Security**: Production-specific middleware and settings
3. **Logging**: Appropriate log levels for each environment
4. **CORS**: Restrictive CORS in production

## Testing

The core module is designed for easy testing:

```python
import pytest
from fastapi.testclient import TestClient
from recommendation_api.core import create_app

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to Next Watch" in response.json()["message"]
```

## Future Enhancements

Planned improvements for the core module:

1. **Authentication Middleware**: JWT and API key authentication
2. **Rate Limiting**: Request rate limiting middleware
3. **Request Logging**: Structured request/response logging
4. **Metrics**: Prometheus metrics collection
5. **Circuit Breaker**: Circuit breaker pattern for external services
6. **Caching**: Response caching middleware
