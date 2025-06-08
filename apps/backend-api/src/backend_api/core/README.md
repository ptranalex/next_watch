***REMOVED*** Backend API Core Module

The `core` module contains the foundational components for the Next Watch Backend API service, implementing a clean Application Factory pattern that separates concerns and promotes maintainability.

***REMOVED******REMOVED*** Architecture Overview

The core module follows modern FastAPI best practices:

```
core/
├── __init__.py      ***REMOVED*** Module exports
├── app.py           ***REMOVED*** Application factory & lifespan
├── middleware.py    ***REMOVED*** Middleware configuration
└── logging.py       ***REMOVED*** Logging setup wrapper
```

***REMOVED******REMOVED*** Components

***REMOVED******REMOVED******REMOVED*** Application Factory (`app.py`)

The heart of the application, implementing the Application Factory pattern for clean separation of concerns and testability.

***REMOVED******REMOVED******REMOVED******REMOVED*** Key Features

- **Lifespan Management**: Handles startup and shutdown of all services
- **Dependency Injection**: Services are initialized and stored in `app.state`
- **Health Service Integration**: Automatic health service initialization
- **Database Connection**: PostgreSQL database initialization
- **Redis Integration**: Optional suggestion engine with graceful fallback
- **Global Exception Handling**: Centralized error handling

***REMOVED******REMOVED******REMOVED******REMOVED*** Lifespan Management

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    ***REMOVED*** Startup sequence:
    ***REMOVED*** 1. Initialize database connection
    ***REMOVED*** 2. Initialize health service
    ***REMOVED*** 3. Initialize suggestion engine (optional)

    yield

    ***REMOVED*** Shutdown sequence:
    ***REMOVED*** 1. Close health service connections
    ***REMOVED*** 2. Close suggestion engine connections
    ***REMOVED*** 3. Close global health service
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Service Initialization

```python
***REMOVED*** Health service - always initialized
health_service = HealthService()
app.state.health_service = health_service

***REMOVED*** Suggestion engine - optional (graceful fallback if Redis unavailable)
if suggestion_service_enabled:
    suggestion_engine = SuggestionEngine(settings.redis_url)
    await suggestion_engine.initialize()
    app.state.suggestion_engine = suggestion_engine
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Application Creation

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

    ***REMOVED*** Setup middleware
    setup_middleware(app)

    ***REMOVED*** Register routers
    app.include_router(meta_router)
    app.include_router(health_router)
    app.include_router(api_v1_router)

    return app
```

***REMOVED******REMOVED******REMOVED*** Middleware Configuration (`middleware.py`)

Centralized middleware setup for clean separation of concerns.

***REMOVED******REMOVED******REMOVED******REMOVED*** CORS Configuration

Configured for microservice architecture where the backend API is called by the BFF:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  ***REMOVED*** Next.js default
        "http://localhost:3001",  ***REMOVED*** Development port
        "http://localhost:3002",  ***REMOVED*** Additional ports
        "http://localhost:8000",  ***REMOVED*** Common development
        "http://127.0.0.1:3000",  ***REMOVED*** Alternative localhost
        "http://127.0.0.1:3001",
    ] + settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization", "Content-Type"],
)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Error Handling

Custom error handling middleware for consistent error responses:

```python
app.add_middleware(ErrorHandlerMiddleware)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Performance Monitoring

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

***REMOVED******REMOVED******REMOVED*** Logging Configuration (`logging.py`)

Thin wrapper around the comprehensive logging configuration in `config/logging.py`.

***REMOVED******REMOVED******REMOVED******REMOVED*** Features

- **Settings Integration**: Uses application settings for log configuration
- **Environment Awareness**: Adapts to debug mode and environment
- **Directory Support**: Optional log directory configuration
- **Clean Interface**: Simple wrapper for complex logging setup

***REMOVED******REMOVED******REMOVED******REMOVED*** Usage

```python
from backend_api.core.logging import setup_logging

***REMOVED*** Use application defaults
setup_logging()

***REMOVED*** Override specific settings
setup_logging(log_level="DEBUG", verbose=True, quiet=False)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Configuration Flow

```python
def setup_logging(log_level=None, verbose=None, quiet=False):
    ***REMOVED*** Use settings defaults if not provided
    if log_level is None:
        log_level = settings.log_level
    if verbose is None:
        verbose = settings.debug

    ***REMOVED*** Determine log directory from settings
    log_dir = None
    if hasattr(settings, "log_dir") and settings.log_dir:
        log_dir = Path(settings.log_dir)

    ***REMOVED*** Configure using comprehensive config module
    _configure_logging(
        log_level=log_level,
        log_dir=log_dir,
        verbose=verbose,
        quiet=quiet,
    )
```

***REMOVED******REMOVED*** Integration with Other Modules

***REMOVED******REMOVED******REMOVED*** Health Service Integration

The core module integrates tightly with the health service:

```python
***REMOVED*** Initialization during startup
health_service = HealthService()
app.state.health_service = health_service

***REMOVED*** Access in routes
health_service = request.app.state.health_service
health_results = await health_service.check_all()

***REMOVED*** Cleanup during shutdown
app.state.health_service.close()
close_health_service()
```

***REMOVED******REMOVED******REMOVED*** Configuration Integration

Seamless integration with the configuration system:

```python
from backend_api.config.app import settings

app = FastAPI(
    title="Next Watch Backend API",
    debug=settings.debug,
    ***REMOVED*** ... other settings
)

***REMOVED*** Middleware uses settings
setup_middleware(app)  ***REMOVED*** Uses settings.cors_origins, etc.

***REMOVED*** Logging uses settings
setup_logging()  ***REMOVED*** Uses settings.log_level, settings.debug
```

***REMOVED******REMOVED******REMOVED*** Route Integration

Clean router registration:

```python
***REMOVED*** Meta routes (root, debug)
app.include_router(meta_router)

***REMOVED*** Health check routes
app.include_router(health_router)

***REMOVED*** API routes
app.include_router(api_v1_router)
```

***REMOVED******REMOVED*** Configuration

The core module is configured through the `backend_api.config.app.settings` object:

***REMOVED******REMOVED******REMOVED*** Required Settings

- `debug`: Boolean for debug mode
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `cors_origins`: List of allowed CORS origins
- `redis_url`: Redis connection URL for suggestion engine

***REMOVED******REMOVED******REMOVED*** Optional Settings

- `log_dir`: Directory for log files
- `enable_performance_metrics`: Enable performance timing headers

***REMOVED******REMOVED*** Usage Examples

***REMOVED******REMOVED******REMOVED*** Basic Application Creation

```python
from backend_api.core.app import create_app

app = create_app()
```

***REMOVED******REMOVED******REMOVED*** Custom Logging Setup

```python
from backend_api.core.logging import setup_logging

***REMOVED*** Setup with custom parameters
setup_logging(log_level="DEBUG", verbose=True)
```

***REMOVED******REMOVED******REMOVED*** Accessing Services in Routes

```python
from fastapi import Request

async def my_route(request: Request):
    ***REMOVED*** Access health service
    health_service = request.app.state.health_service
    if health_service:
        results = await health_service.check_all()

    ***REMOVED*** Access suggestion engine
    suggestion_engine = getattr(request.app.state, "suggestion_engine", None)
    if suggestion_engine:
        suggestions = await suggestion_engine.get_suggestions(user_id)
```

***REMOVED******REMOVED*** Testing

***REMOVED******REMOVED******REMOVED*** Unit Testing

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
    assert response.status_code in [200, 503]  ***REMOVED*** Depends on service availability
```

***REMOVED******REMOVED******REMOVED*** Integration Testing

```python
@pytest.mark.asyncio
async def test_lifespan():
    app = create_app()

    ***REMOVED*** Test startup
    async with lifespan(app):
        assert hasattr(app.state, "health_service")
        assert app.state.health_service is not None

        ***REMOVED*** Test service functionality
        results = await app.state.health_service.check_all()
        assert "postgres" in results
```

***REMOVED******REMOVED*** Best Practices

***REMOVED******REMOVED******REMOVED*** Service Initialization

1. **Graceful Fallback**: Services should fail gracefully if dependencies aren't available
2. **State Management**: Store services in `app.state` for global access
3. **Cleanup**: Always clean up resources during shutdown

***REMOVED******REMOVED******REMOVED*** Error Handling

1. **Global Handler**: Use global exception handler for unhandled exceptions
2. **Logging**: Log errors with appropriate detail level
3. **User-Friendly**: Return user-friendly error messages

***REMOVED******REMOVED******REMOVED*** Configuration

1. **Environment Aware**: Adapt behavior based on environment (dev/prod)
2. **Validation**: Validate configuration at startup
3. **Security**: Mask sensitive information in logs

***REMOVED******REMOVED*** Future Enhancements

***REMOVED******REMOVED******REMOVED*** Planned Features

1. **Metrics Integration**: Prometheus metrics collection
2. **Tracing**: OpenTelemetry distributed tracing
3. **Rate Limiting**: Request rate limiting middleware
4. **Circuit Breaker**: Circuit breaker for external service calls
5. **Caching**: Response caching middleware

***REMOVED******REMOVED******REMOVED*** Scalability Considerations

1. **Connection Pooling**: Optimize database and Redis connection pools
2. **Async Services**: Convert more services to async for better performance
3. **Load Balancing**: Health checks optimized for load balancer integration
4. **Monitoring**: Enhanced monitoring and alerting capabilities

***REMOVED******REMOVED*** Dependencies

***REMOVED******REMOVED******REMOVED*** Required

- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `sqlmodel`: Database ORM
- `redis`: Redis client (optional)

***REMOVED******REMOVED******REMOVED*** Optional

- `redis`: For suggestion engine functionality
- `prometheus-client`: For metrics collection
- `opentelemetry`: For distributed tracing

The core module provides a solid foundation for the Backend API service with clean separation of concerns, comprehensive error handling, and excellent testability.
