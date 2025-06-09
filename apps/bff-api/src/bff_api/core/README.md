***REMOVED*** BFF Core Module

The core module contains the foundational components of the Next Watch BFF (Backend for Frontend) service, implementing a clean and maintainable Application Factory pattern.

***REMOVED******REMOVED*** Overview

The BFF service acts as an aggregation layer between frontend applications and backend microservices, providing:

- **Data Aggregation**: Combines data from multiple backend services
- **Request/Response Transformation**: Formats data for frontend consumption
- **Authentication Proxy**: Handles user authentication and authorization
- **Caching Layer**: Optimizes performance through intelligent caching
- **Error Handling**: Provides consistent error responses
- **API Versioning**: Supports multiple API versions for frontend compatibility

***REMOVED******REMOVED*** Architecture

The core module follows the **Application Factory pattern**, providing clean separation of concerns and dependency injection:

```
bff_api/core/
├── __init__.py      ***REMOVED*** Module exports
├── app.py           ***REMOVED*** Application factory and lifecycle management
├── middleware.py    ***REMOVED*** Middleware configuration
└── logging.py       ***REMOVED*** Logging setup
```

***REMOVED******REMOVED*** Components

***REMOVED******REMOVED******REMOVED*** Application Factory (`app.py`)

The main application factory provides:

***REMOVED******REMOVED******REMOVED******REMOVED*** **Lifespan Management**

- **Startup**: Initializes backend clients, auth clients, and health service
- **Shutdown**: Gracefully closes all connections and resources
- **Error Handling**: Robust error handling during startup/shutdown

```python
from bff_api.core import create_app

app = create_app()
```

***REMOVED******REMOVED******REMOVED******REMOVED*** **Service Integration**

- **Backend Client**: HTTP client for main backend API
- **Auth Client**: Authentication service client
- **Health Service**: External dependency monitoring
- **Graceful Fallbacks**: Continues operation if non-critical services fail

***REMOVED******REMOVED******REMOVED******REMOVED*** **Route Registration**

- **Meta Routes**: Root endpoint and debug information (`/`, `/debug`)
- **Health Routes**: Comprehensive health monitoring (`/health/*`)
- **API Routes**: Versioned BFF endpoints (`/bff/v1/*`)

***REMOVED******REMOVED******REMOVED******REMOVED*** **Global Exception Handling**

- Catches and logs unhandled exceptions
- Returns consistent error responses
- Prevents service crashes from unexpected errors

***REMOVED******REMOVED******REMOVED*** Middleware Configuration (`middleware.py`)

Configures all middleware in the correct order:

***REMOVED******REMOVED******REMOVED******REMOVED*** **CORS Middleware**

- Critical for frontend applications
- Configurable origins from settings
- Supports credentials and custom headers

***REMOVED******REMOVED******REMOVED******REMOVED*** **Security Middleware**

- **Trusted Host**: Prevents host header attacks in production
- **Authentication**: JWT token validation and user context
- **Request Logging**: Comprehensive request/response logging

***REMOVED******REMOVED******REMOVED******REMOVED*** **Performance Middleware**

- Optional performance metrics collection
- Response timing headers
- Service identification headers

***REMOVED******REMOVED******REMOVED******REMOVED*** **Configuration Example**

```python
***REMOVED*** Development - Allow specific origins
CORS_ORIGINS = "http://localhost:3000,http://localhost:8001"

***REMOVED*** Production - Restrict to frontend domain
CORS_ORIGINS = "https://nextwatch.com"
```

***REMOVED******REMOVED******REMOVED*** Logging Setup (`logging.py`)

Provides a clean interface to the comprehensive logging system:

```python
from bff_api.core.logging import setup_logging

***REMOVED*** Basic setup
setup_logging()

***REMOVED*** Advanced setup
setup_logging(
    log_level="DEBUG",
    verbose=True,
    quiet=False
)
```

***REMOVED******REMOVED*** Lifecycle Management

***REMOVED******REMOVED******REMOVED*** Startup Sequence

1. **Environment Setup**: Load configuration and environment variables
2. **Logging Initialization**: Configure logging based on environment
3. **Service Creation**: Initialize backend clients and health service
4. **Middleware Setup**: Configure all middleware in correct order
5. **Route Registration**: Register all API routes and endpoints
6. **Health Checks**: Verify external service connectivity

***REMOVED******REMOVED******REMOVED*** Shutdown Sequence

1. **Health Service**: Close health monitoring connections
2. **Backend Client**: Close HTTP client connections
3. **Auth Client**: Close authentication service connections
4. **Global Cleanup**: Close any remaining global resources

***REMOVED******REMOVED*** Integration with Services

***REMOVED******REMOVED******REMOVED*** Backend Client Integration

The BFF integrates with the main backend API:

```python
***REMOVED*** Access in route handlers
async def get_movies(request: Request):
    backend_client = request.app.state.backend_client
    movies = await backend_client.get_movies()
    return movies
```

***REMOVED******REMOVED******REMOVED*** Health Service Integration

Comprehensive monitoring of external dependencies:

```python
***REMOVED*** External service health checks
health_service = request.app.state.health_service
if health_service:
    results = await health_service.check_all()
    ***REMOVED*** Check backend_api, recommendation_api, auth_api
```

***REMOVED******REMOVED******REMOVED*** Authentication Integration

JWT token validation and user context:

```python
***REMOVED*** Access authenticated user
user = request.state.user  ***REMOVED*** Set by AuthMiddleware
if user:
    ***REMOVED*** Handle authenticated requests
```

***REMOVED******REMOVED*** Configuration

The core module uses the centralized configuration system:

```python
from bff_api.config.app import settings

***REMOVED*** Service URLs
settings.backend_api_url     ***REMOVED*** Main backend API
settings.reco_api_url        ***REMOVED*** Recommendation service
settings.auth_api_url        ***REMOVED*** Authentication service

***REMOVED*** Security
settings.cors_origins        ***REMOVED*** CORS allowed origins
settings.allowed_hosts       ***REMOVED*** Trusted hosts for production
settings.jwt_secret          ***REMOVED*** JWT validation secret

***REMOVED*** Performance
settings.enable_performance_metrics  ***REMOVED*** Performance monitoring
settings.cache_ttl           ***REMOVED*** Cache TTL for responses
```

***REMOVED******REMOVED*** Error Handling

***REMOVED******REMOVED******REMOVED*** Global Exception Handler

All unhandled exceptions are caught and logged:

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

***REMOVED******REMOVED******REMOVED*** Service-Level Error Handling

Individual services handle their own errors gracefully:

- **Backend Client**: Retries with exponential backoff
- **Auth Client**: Graceful authentication failures
- **Health Service**: Non-blocking health checks

***REMOVED******REMOVED*** Testing

***REMOVED******REMOVED******REMOVED*** Unit Testing

Test the application factory:

```python
from bff_api.core import create_app

def test_app_creation():
    app = create_app()
    assert app.title == "Next Watch BFF"
    assert app.version == "0.1.0"
```

***REMOVED******REMOVED******REMOVED*** Integration Testing

Test with real services:

```python
@pytest.mark.asyncio
async def test_health_endpoint():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code in [200, 503]
```

***REMOVED******REMOVED*** Best Practices

***REMOVED******REMOVED******REMOVED*** Development

1. **Use Debug Mode**: Enable detailed logging and error information
2. **Mock External Services**: Use test doubles for backend services
3. **Monitor Health Checks**: Watch for external service connectivity issues

***REMOVED******REMOVED******REMOVED*** Production

1. **Security Configuration**:

   - Set specific CORS origins
   - Enable trusted host middleware
   - Use secure JWT secrets

2. **Performance Optimization**:

   - Enable performance metrics
   - Configure appropriate cache TTL
   - Monitor response times

3. **Monitoring**:
   - Use health endpoints for load balancer checks
   - Monitor external service connectivity
   - Track authentication failures

***REMOVED******REMOVED******REMOVED*** Debugging

1. **Logging**: Use structured logging for better debugging
2. **Debug Endpoint**: Access `/debug` for configuration information
3. **Health Checks**: Use `/health` to verify external service status

***REMOVED******REMOVED*** Future Enhancements

1. **Rate Limiting**: Add request rate limiting middleware
2. **Circuit Breaker**: Implement circuit breaker pattern for external services
3. **Metrics Collection**: Enhanced metrics collection and exporters
4. **Request Tracing**: Distributed tracing integration
5. **Response Caching**: Intelligent response caching strategies
