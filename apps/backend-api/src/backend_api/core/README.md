# Backend API Core Module

The `core` module contains the foundational components for the Next Watch Backend API service, implementing a clean Application Factory pattern that separates concerns and promotes maintainability.

## Architecture Overview

The core module follows modern FastAPI best practices:

```text
core/
├── __init__.py      # Module exports
├── app.py           # Application factory & lifespan
└── middleware.py    # Middleware configuration
```

> **📦 Migration Notice**: Logging configuration has been moved to the shared NextWatch config library (`config.logging`). The local logging wrapper has been removed in favor of direct usage.

## Components

### Application Factory (`app.py`)

The heart of the application, implementing the Application Factory pattern for clean separation of concerns and testability.

#### Key Features

- **Lifespan Management**: Handles startup and shutdown of all services
- **Dependency Injection**: Services are initialized and stored in `app.state`
- **Health Service Integration**: Automatic health service initialization
- **Database Connection**: PostgreSQL database initialization
- **Redis Integration**: Optional suggestion engine with graceful fallback
- **Global Exception Handling**: Centralized error handling

#### Lifespan Management

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup sequence:
    # 1. Initialize database connection
    # 2. Initialize health service
    # 3. Initialize suggestion engine (optional)

    yield

    # Shutdown sequence:
    # 1. Close health service connections
    # 2. Close suggestion engine connections
    # 3. Close global health service
```

#### Service Initialization Example

```python
# Health service - always initialized
health_service = HealthService()
app.state.health_service = health_service

# Suggestion engine - optional (graceful fallback if Redis unavailable)
if suggestion_service_enabled:
    suggestion_engine = SuggestionEngine(settings.redis_url)
    await suggestion_engine.initialize()
    app.state.suggestion_engine = suggestion_engine
```

#### Application Creation

```python
def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Next Watch Backend API",
        description="Backend for Frontend API for serving movie data and user interactions",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Setup middleware
    setup_middleware(app)

    # Register routers
    app.include_router(meta_router)
    app.include_router(health_router)
    app.include_router(api_v1_router)

    return app
```

### Middleware Configuration (`middleware.py`)

Centralized middleware setup for clean separation of concerns.

#### CORS Configuration

Configured for microservice architecture where the backend API is called by the BFF:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js default
        "http://localhost:3001",  # Development port
        "http://localhost:3002",  # Additional ports
        "http://localhost:8000",  # Common development
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://127.0.0.1:3001",
    ] + settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization", "Content-Type"],
)
```

#### Error Handling Example

Custom error handling middleware for consistent error responses:

```python
app.add_middleware(ErrorHandlerMiddleware)
```

#### Performance Monitoring

Optional performance timing middleware:

```python
if settings.enable_performance_metrics:
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next: Any):
        start_time = datetime.datetime.now()
        response = await call_next(request)
        process_time = (datetime.datetime.now() - start_time).total_seconds()
        response.headers["X-Process-Time"] = str(process_time)
        return response
```

### Logging Configuration (Shared Library)

Logging is now handled directly through the shared NextWatch config library (`config.logging`).

#### Direct Usage

```python
from config.logging import configure_logging, get_logger

# Configure logging with service identity
configure_logging(
    log_level="DEBUG",
    logger_name="backend_api",
    verbose=True,
    color_theme="modern"
)

# Get hierarchical loggers
logger = get_logger(__name__)  # Creates "backend_api.core.app"
logger.info("Application starting", port=8001)
```

#### Benefits

- **No Wrapper Overhead**: Direct access to shared library functionality
- **Hierarchical Logging**: Using `__name__` creates proper logger hierarchy
- **Consistent**: Same logging setup across all NextWatch services
- **Full Featured**: Access to all color themes, HTTP verbosity controls, etc.

## Integration with Other Modules

### Health Service Integration

The core module integrates tightly with the health service:

```python
# Initialization during startup
health_service = HealthService()
app.state.health_service = health_service

# Access in routes
health_service = request.app.state.health_service
health_results = await health_service.check_all()

# Cleanup during shutdown
app.state.health_service.close()
close_health_service()
```

### Configuration Integration

Seamless integration with the configuration system:

```python
from backend_api.config.app import settings

app = FastAPI(
    title="Next Watch Backend API",
    debug=settings.debug,
    # ... other settings
)

# Middleware uses settings
setup_middleware(app)  # Uses settings.cors_origins, etc.

# Logging configured at startup
configure_logging(log_level=settings.log_level, logger_name="backend_api")
```

### Route Integration

Clean router registration:

```python
# Meta routes (root, debug)
app.include_router(meta_router)

# Health check routes
app.include_router(health_router)

# API routes
app.include_router(api_v1_router)
```

## Configuration

The core module is configured through the NextWatch shared configuration library with `BackendAPIConfig`:

### Configuration Mixins

- **ServiceConfig**: HTTP service settings (port, debug mode)
- **DatabaseConfigMixin**: PostgreSQL connection configuration
- **CacheConfigMixin**: Redis configuration for suggestion engine
- **AuthConfigMixin**: JWT authentication settings
- **MonitoringConfigMixin**: Logging and metrics configuration

### Key Settings

- `debug`: Boolean for debug mode
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `cors_origins`: List of allowed CORS origins (defaults to ["*"] for development)
- `redis_url`: Redis connection URL for suggestion engine
- `database_url`: PostgreSQL connection string
- `jwt_secret`: JWT signing secret
- `enable_performance_metrics`: Enable performance timing headers

### Environment Variables

Configuration is loaded from environment variables with fallbacks:

- `DATABASE_URL`: PostgreSQL connection
- `REDIS_URL`: Redis connection
- `JWT_SECRET`: JWT signing secret
- `LOG_LEVEL`: Logging verbosity
- `DEBUG`: Development mode flag

## Usage Examples

### Basic Application Creation

```python
from backend_api.core.app import create_app
from config.logging import configure_logging

# Configure logging first
configure_logging(logger_name="backend_api")

# Create application
app = create_app()
```

### Custom Logging Setup

```python
from config.logging import configure_logging, get_logger

# Configure with service identity and options
configure_logging(
    log_level="DEBUG",
    logger_name="backend_api",
    verbose=True,
    color_theme="modern"
)

# Get logger for specific module
logger = get_logger(__name__)
```

### Accessing Services in Routes

```python
from fastapi import Request

async def my_route(request: Request):
    # Access health service
    health_service = request.app.state.health_service
    if health_service:
        results = await health_service.check_all()

    # Access suggestion engine
    suggestion_engine = getattr(request.app.state, "suggestion_engine", None)
    if suggestion_engine:
        suggestions = await suggestion_engine.get_suggestions(user_id)
```

## Testing

### Unit Testing

```python
import pytest
from backend_api.core.app import create_app

@pytest.fixture
def app():
    return create_app()

@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient
    return TestClient(app)

def test_app_creation():
    app = create_app()
    assert app.title == "Next Watch Backend API"
    assert app.version == "0.1.0"

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code in [200, 503]  # Depends on service availability
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_lifespan():
    app = create_app()

    # Test startup
    async with lifespan(app):
        assert hasattr(app.state, "health_service")
        assert app.state.health_service is not None

        # Test service functionality
        results = await app.state.health_service.check_all()
        assert "postgres" in results
```

## Best Practices

### Service Initialization

1. **Graceful Fallback**: Services should fail gracefully if dependencies aren't available
2. **State Management**: Store services in `app.state` for global access
3. **Cleanup**: Always clean up resources during shutdown

### Error Handling

1. **Global Handler**: Use global exception handler for unhandled exceptions
2. **Logging**: Log errors with appropriate detail level
3. **User-Friendly**: Return user-friendly error messages

### Configuration Best Practices

1. **Environment Aware**: Adapt behavior based on environment (dev/prod)
2. **Validation**: Validate configuration at startup
3. **Security**: Mask sensitive information in logs

## Future Enhancements

### Planned Features

1. **Metrics Integration**: Prometheus metrics collection
2. **Tracing**: OpenTelemetry distributed tracing
3. **Rate Limiting**: Request rate limiting middleware
4. **Circuit Breaker**: Circuit breaker for external service calls
5. **Caching**: Response caching middleware

### Scalability Considerations

1. **Connection Pooling**: Optimize database and Redis connection pools
2. **Async Services**: Convert more services to async for better performance
3. **Load Balancing**: Health checks optimized for load balancer integration
4. **Monitoring**: Enhanced monitoring and alerting capabilities

## Dependencies

### Required

- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `sqlmodel`: Database ORM
- `config @ file:../../libs/config`: NextWatch shared configuration library

### Optional

- `redis`: For suggestion engine functionality
- `prometheus-client`: For metrics collection
- `opentelemetry`: For distributed tracing

### Shared Libraries

- **Config Library**: Type-safe configuration with Pydantic Settings
- **Movie Storage**: Shared data models and database operations

The core module provides a solid foundation for the Backend API service with clean separation of concerns, comprehensive error handling, and excellent testability. It leverages the NextWatch shared configuration library for type-safe, environment-aware configuration management and consistent logging across all services.
