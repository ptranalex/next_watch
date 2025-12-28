***REMOVED*** Fast Core

A comprehensive core library for building standardized FastAPI applications across Next Watch services. Fast Core provides common patterns, utilities, and components that ensure consistency and reduce boilerplate code.

***REMOVED******REMOVED*** Overview

Fast Core standardizes FastAPI application development by providing:

- **Application Factory**: Consistent app creation with standardized configuration
- **Dependency Injection**: Common dependencies for auth, database, cache, and more
- **Error Handling**: Comprehensive exception handling and standardized error responses
- **Security**: JWT authentication, rate limiting, and security headers
- **Middleware**: CORS, logging, security, metrics, and tracing
- **Routing**: API versioning, pagination, and base router utilities
- **Monitoring**: Health checks, system monitoring, and comprehensive metrics collection

***REMOVED******REMOVED*** Quick Start

***REMOVED******REMOVED******REMOVED*** Installation

```bash
***REMOVED*** Install from local development
pip install -e libs/fast-core

***REMOVED*** Or add to pyproject.toml
[tool.hatch.envs.default.dependencies]
fast-core = {path = "libs/fast-core", develop = true}
```

***REMOVED******REMOVED******REMOVED*** Basic Usage

```python
from fastapi import FastAPI, Depends
from fast_core import create_app, FastAPIConfig
from fast_core.dependencies import get_current_user, get_pagination_params
from fast_core.routing.pagination import paginate_results

***REMOVED*** Configure the application
config = FastAPIConfig(
    title="My API",
    version="1.0.0",
    database_url="postgresql://user:pass@localhost/db",
    redis_url="redis://localhost:6379",
    jwt_secret_key="your-secret-key"
)

***REMOVED*** Create FastAPI app with all Fast Core features
app = create_app(config=config)

***REMOVED*** Use Fast Core dependencies
@app.get("/users")
async def list_users(
    pagination = Depends(get_pagination_params),
    current_user = Depends(get_current_user)
):
    users = await get_users_from_db(
        offset=pagination.offset,
        limit=pagination.limit
    )
    total_count = await count_users()

    return paginate_results(
        data=users,
        pagination=pagination,
        total_count=total_count
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

***REMOVED******REMOVED*** Module Documentation

Each complex module has its own comprehensive README with examples and best practices:

***REMOVED******REMOVED******REMOVED*** 📁 [Dependencies](src/fast_core/dependencies/README.md)

Dependency injection utilities for FastAPI applications:

- **Common**: Request metadata, pagination, search parameters
- **Authentication**: API key validation, user authentication, role-based authorization
- **Database**: Session management, transactions, read-only access
- **Cache**: Redis client, cache manager, cache service operations

***REMOVED******REMOVED******REMOVED*** 🔒 [Security](src/fast_core/security/README.md)

Security utilities for authentication and protection:

- **JWT Management**: Token creation, validation, and refresh handling
- **Rate Limiting**: Request throttling with memory and Redis backends

***REMOVED******REMOVED******REMOVED*** ❌ [Errors](src/fast_core/errors/README.md)

Comprehensive error handling system:

- **Exceptions**: Custom exception classes for different error types
- **Handlers**: Exception handlers that convert exceptions to HTTP responses
- **Responses**: Standardized error response models and utilities

***REMOVED******REMOVED******REMOVED*** 🛡️ [Middleware](src/fast_core/middleware/README.md)

Essential middleware components with builder pattern configuration:

- **CORS**: Cross-Origin Resource Sharing with specific origins, methods, and headers
- **Security Headers**: HSTS, CSP, frame options, XSS protection, and trusted hosts
- **Rate Limiting**: Per-endpoint rate limits with Redis support and IP exemptions
- **Request Logging**: Configurable request/response logging with filtering
- **Request Processing**: Request IDs, timing headers, compression, and size limits
- **Metrics Collection**: Prometheus metrics for requests, responses, errors, and performance

***REMOVED******REMOVED******REMOVED*** 📊 [Monitoring](src/fast_core/monitoring/README.md)

Comprehensive monitoring and observability features:

- **Prometheus Metrics**: Request duration, error rates, response sizes, and custom metrics
- **Health Checks**: Service health monitoring with dependency validation
- **Performance Tracking**: Response times, throughput, and resource utilization
- **Error Monitoring**: Exception tracking, error rates, and failure analysis

***REMOVED******REMOVED******REMOVED*** 🛣️ [Routing](src/fast_core/routing/README.md)

Advanced routing utilities:

- **Pagination**: Comprehensive pagination with metadata and response formatting
- **Versioning**: Multi-strategy API versioning (URL, header, query, accept)
- **Base Router**: Foundation router class with common functionality

***REMOVED******REMOVED*** Features

***REMOVED******REMOVED******REMOVED*** Application Factory

```python
from fast_core import create_app, AppOptions
from fast_core.middleware import MiddlewareConfig

***REMOVED*** Basic app creation
app = create_app()

***REMOVED*** Advanced configuration with middleware builder
middleware = MiddlewareConfig()
middleware.cors(
    origins=["https://app.example.com"],
    credentials=True
).security_headers(
    hsts=True,
    csp="default-src 'self'"
).rate_limiting(
    default_limit="100/minute",
    endpoints={"/api/auth/login": "5/minute"}
).metrics(
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    exclude_paths=["/health", "/metrics"]
)

app = create_app(
    config=FastAPIConfig(
        title="My API",
        version="1.0.0",
        debug=False
    ),
    middleware=middleware
)
```

***REMOVED******REMOVED******REMOVED*** Metrics Integration

```python
from fast_core.monitoring.metrics import (
    REQUESTS_TOTAL, REQUEST_DURATION_SECONDS, track_operation
)

***REMOVED*** Track custom operations
@track_operation("user_creation")
async def create_user(user_data: dict):
    ***REMOVED*** Custom metrics are automatically collected
    return await db.create_user(user_data)

***REMOVED*** Access built-in metrics
@app.get("/api/v1/movies")
async def get_movies():
    ***REMOVED*** Request metrics automatically tracked:
    ***REMOVED*** - http_requests_total{method="GET", endpoint="/api/v1/movies", status="200"}
    ***REMOVED*** - http_request_duration_seconds{method="GET", endpoint="/api/v1/movies"}
    ***REMOVED*** - http_response_size_bytes{method="GET", endpoint="/api/v1/movies"}
    return {"movies": []}

***REMOVED*** View metrics at /metrics endpoint (Prometheus format)
***REMOVED*** Example metrics output:
***REMOVED*** http_requests_total{method="GET",endpoint="/api/v1/movies",status="200"} 150
***REMOVED*** http_request_duration_seconds_bucket{method="GET",endpoint="/api/v1/movies",le="0.1"} 120
***REMOVED*** http_response_size_bytes{method="GET",endpoint="/api/v1/movies"} 2048
```

***REMOVED******REMOVED******REMOVED*** Singleton Dependencies

```python
from fast_core.dependencies.singleton import get_singleton_client, singleton_lifespan

***REMOVED*** Create singleton service clients for performance
@get_singleton_client("database")
def create_database_client() -> DatabaseClient:
    return DatabaseClient("postgresql://localhost/db")

***REMOVED*** Use in FastAPI with automatic cleanup
app = FastAPI(lifespan=singleton_lifespan)

@app.get("/users")
async def get_users(db: DatabaseClient = Depends(create_database_client)):
    return await db.query("SELECT * FROM users")
```

***REMOVED******REMOVED******REMOVED*** Service Client Factory (NEW!)

```python
from fast_core.dependencies.client_factory import (
    register_service, get_service_client, BaseServiceClient, service_client
)

***REMOVED*** Register services with the factory
register_service(
    name="user-service",
    base_url="https://api.users.com",
    timeout=30,
    singleton=True,  ***REMOVED*** Use singleton for performance
    headers={"Authorization": "Bearer token"}
)

***REMOVED*** Create custom service clients
class UserServiceClient(BaseServiceClient):
    async def get_user(self, user_id: int):
        client = await self._get_client()
        response = await client.get(f"/users/{user_id}")
        return response.json()

***REMOVED*** Register with decorator
@service_client("notification-service", singleton=True)
class NotificationClient(BaseServiceClient):
    async def send_notification(self, user_id: int, message: str):
        client = await self._get_client()
        return await client.post("/notify", json={"user_id": user_id, "message": message})

***REMOVED*** Use in FastAPI endpoints
get_user_client = get_service_client("user-service")

@app.get("/users/{user_id}")
async def get_user(user_id: int, client: UserServiceClient = Depends(get_user_client)):
    return await client.get_user(user_id)
```

***REMOVED******REMOVED******REMOVED*** Comprehensive Error Handling

```python
from fast_core.errors.exceptions import (
    ValidationException,
    ResourceNotFoundException,
    AuthorizationException
)

***REMOVED*** Raise specific exceptions
if not user:
    raise ResourceNotFoundException(
        message="User not found",
        resource_type="User",
        resource_id=user_id
    )

***REMOVED*** Automatic conversion to HTTP responses
***REMOVED*** Returns: {"error": {"message": "User not found", "code": "USER_NOT_FOUND", ...}}
```

***REMOVED******REMOVED******REMOVED*** JWT Authentication

```python
from fast_core.security.jwt import create_jwt_manager, JWTConfig

***REMOVED*** Configure JWT
jwt_config = JWTConfig(
    secret_key="your-secret-key",
    access_token_expire_minutes=30
)
jwt_manager = create_jwt_manager(jwt_config)

***REMOVED*** Create and verify tokens
access_token = jwt_manager.create_access_token({"sub": "user123"})
payload = jwt_manager.verify_token(access_token)
```

***REMOVED******REMOVED******REMOVED*** Rate Limiting

```python
from fast_core.security.rate_limit import RedisRateLimiter, rate_limit

***REMOVED*** Create rate limiter
limiter = RedisRateLimiter(redis_url="redis://localhost:6379")

***REMOVED*** Apply rate limiting
@rate_limit(limiter=limiter, max_requests=100, window_seconds=3600)
async def my_endpoint():
    return {"message": "Success"}
```

***REMOVED******REMOVED******REMOVED*** API Versioning

```python
from fast_core.routing.versioning import VersionedRouter

***REMOVED*** Create versioned router
router = VersionedRouter(prefix="/api", strategy="url_path")

@router.get("/users", version="v1")
async def list_users_v1():
    return {"users": [], "version": "v1"}

@router.get("/users", version="v2")
async def list_users_v2():
    return {"users": [], "version": "v2", "enhanced": True}
```

***REMOVED******REMOVED******REMOVED*** Pagination

```python
from fast_core.routing.pagination import get_pagination_params, paginate_results

@app.get("/users")
async def list_users(pagination = Depends(get_pagination_params)):
    users = await get_users(offset=pagination.offset, limit=pagination.limit)
    total_count = await count_users()

    return paginate_results(
        data=users,
        pagination=pagination,
        total_count=total_count
    )
```

***REMOVED******REMOVED*** Configuration

Fast Core uses environment-based configuration:

```bash
***REMOVED*** Database
DATABASE_URL=postgresql://user:pass@localhost/db

***REMOVED*** Redis
REDIS_URL=redis://localhost:6379

***REMOVED*** JWT
JWT_SECRET_KEY=your-256-bit-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

***REMOVED*** CORS
CORS_ORIGINS=https://example.com,https://app.example.com

***REMOVED*** Security
SECURITY_HSTS_MAX_AGE=31536000
RATE_LIMIT_MAX_REQUESTS=1000

***REMOVED*** Monitoring
METRICS_ENABLED=true
METRICS_INCLUDE_REQUEST_SIZE=true
METRICS_INCLUDE_RESPONSE_SIZE=true
METRICS_BUCKETS=0.1,0.25,0.5,1.0,2.5,5.0,10.0

***REMOVED*** Logging
LOG_LEVEL=INFO
```

***REMOVED******REMOVED*** Integration with Next Watch Services

Fast Core is designed to work seamlessly with other Next Watch libraries:

- **Config Library**: Environment-based configuration loading
- **Cache Library**: Redis and memory caching integration
- **CLI Library**: Command-line utilities and structured logging
- **Movie Storage**: Database models and operations

***REMOVED******REMOVED******REMOVED*** Production Metrics Integration

Fast Core's metrics system is successfully deployed across all NextWatch services in production:

***REMOVED******REMOVED******REMOVED******REMOVED*** **Deployed Services with Metrics** ✅

- **BFF API** (`bff-api:8001/metrics`) - API gateway with authentication, caching, and service orchestration metrics
- **Backend API** (`backend-api:8002/metrics`) - Core movie data operations and database performance metrics
- **Search API** (`search-api:8003/metrics`) - Search operations, Redis performance, and query analytics metrics
- **Recommendation API** (`recommendation-api:8004/metrics`) - ML-powered recommendations, vector operations, and personalization metrics
- **Auth API** (`auth-api:8005/metrics`) - Authentication, JWT operations, and security metrics

***REMOVED******REMOVED******REMOVED******REMOVED*** **Metrics Categories**

Each service collects comprehensive metrics across these categories:

1. **HTTP Request Metrics**:

   - Request volume, latency, and error rates by endpoint
   - Response sizes and status code distributions
   - Rate limiting and throttling statistics

2. **Service-Specific Operations**:

   - **BFF**: Service orchestration, cache hit rates, authentication flows
   - **Backend**: Database queries, movie operations, collection management
   - **Search**: Search queries, suggestion generation, Redis operations
   - **Recommendation**: ML API calls, vector searches, personalization features
   - **Auth**: JWT operations, user authentication, session management

3. **Infrastructure Metrics**:

   - Redis connection pools and operation timing
   - Database connection health and query performance
   - External service dependencies and health checks

4. **Business Metrics**:
   - Feature usage patterns and user interaction analytics
   - Error categorization and failure analysis
   - Performance benchmarking and SLA monitoring

***REMOVED******REMOVED******REMOVED******REMOVED*** **Prometheus Configuration**

All services are automatically discovered and scraped by Prometheus:

```yaml
***REMOVED*** Production prometheus.yml
scrape_configs:
  - job_name: "nextwatch-services"
    static_configs:
      - targets:
          [
            "bff-api:8001",
            "backend-api:8002",
            "search-api:8003",
            "recommendation-api:8004",
            "auth-api:8005",
          ]
    metrics_path: "/metrics"
    scrape_interval: 15s
```

***REMOVED******REMOVED******REMOVED******REMOVED*** **Grafana Dashboards**

Production monitoring includes specialized dashboards for:

- **Service Performance**: Request latency, throughput, error rates
- **Infrastructure Health**: Redis, database, and service dependency status
- **Business Intelligence**: User engagement, feature adoption, recommendation effectiveness
- **Security Monitoring**: Authentication patterns, rate limiting, and security events

This comprehensive metrics integration provides full observability across the NextWatch platform, enabling proactive monitoring, performance optimization, and business intelligence.

***REMOVED******REMOVED*** Best Practices

***REMOVED******REMOVED******REMOVED*** Application Structure

```python
***REMOVED*** main.py
from fast_core import create_app, FastAPIConfig
from .routers import users, movies
from .config import get_config

***REMOVED*** Load configuration
config = get_config()

***REMOVED*** Create app with Fast Core
app = create_app(config=config)

***REMOVED*** Include routers
app.include_router(users.router)
app.include_router(movies.router)
```

***REMOVED******REMOVED******REMOVED*** Error Handling

```python
***REMOVED*** Use specific exceptions
from fast_core.errors.exceptions import ValidationException

if not email_is_valid(email):
    raise ValidationException(
        message="Invalid email format",
        field="email",
        value=email
    )
```

***REMOVED******REMOVED******REMOVED*** Security

```python
***REMOVED*** Combine authentication and authorization
from fast_core.dependencies.auth import get_current_user, require_roles

@app.get("/admin/users")
async def admin_users(
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["admin"]))
):
    ***REMOVED*** Only authenticated admins can access
    pass
```

***REMOVED******REMOVED******REMOVED*** Database Operations

```python
***REMOVED*** Use appropriate session types
from fast_core.dependencies.database import get_db_transaction, get_readonly_db_session

@app.post("/users")
async def create_user(
    user_data: UserCreate,
    db = Depends(get_db_transaction)  ***REMOVED*** Auto-commits
):
    ***REMOVED*** Database changes are automatically committed
    pass

@app.get("/users")
async def list_users(
    db = Depends(get_readonly_db_session)  ***REMOVED*** Read-only
):
    ***REMOVED*** Cannot modify database
    pass
```

***REMOVED******REMOVED*** Testing

Fast Core components are designed to be easily testable:

```python
from fastapi.testclient import TestClient
from fast_core.dependencies import get_current_user

***REMOVED*** Override dependencies for testing
def override_get_current_user():
    return User(id=1, username="testuser")

app.dependency_overrides[get_current_user] = override_get_current_user

***REMOVED*** Test with client
client = TestClient(app)
response = client.get("/users")
assert response.status_code == 200
```

***REMOVED******REMOVED*** Examples

See the [examples](examples/) directory for complete application examples:

- **Basic App**: Simple FastAPI application with Fast Core
- **Advanced App**: Full-featured application with all Fast Core components

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Running Tests

```bash
***REMOVED*** Run all tests
pytest

***REMOVED*** Run with coverage
pytest --cov=fast_core --cov-report=html

***REMOVED*** Run specific test file
pytest tests/test_dependencies.py
```

***REMOVED******REMOVED******REMOVED*** Type Checking

```bash
***REMOVED*** Run mypy
mypy src/fast_core

***REMOVED*** Run with strict mode
mypy --strict src/fast_core
```

***REMOVED******REMOVED******REMOVED*** Linting

```bash
***REMOVED*** Run ruff
ruff check src/fast_core

***REMOVED*** Auto-fix issues
ruff check --fix src/fast_core
```

***REMOVED******REMOVED*** 🚀 Enhancement Roadmap

Based on real-world integration experience with the BFF API, the following enhancements are planned to make Fast Core even more powerful and developer-friendly:

***REMOVED******REMOVED******REMOVED*** **Phase 1: Core Patterns** (High Priority)

***REMOVED******REMOVED******REMOVED******REMOVED*** **1. Singleton Dependency Pattern** ⭐ **IMMEDIATE**

**Problem**: Current service clients are per-request, but many services need singleton patterns for performance optimization.

**Solution**: Add singleton dependency support:

```python
***REMOVED*** Proposed API
from fast_core.dependencies import get_singleton_client, SingletonConfig

@get_singleton_client("backend", lifecycle="app")
def create_backend_client(config: FastAPIConfig) -> BackendClient:
    return BackendClient(config)

***REMOVED*** Usage in routes
async def get_movies(
    backend: BackendClient = Depends(get_backend_client),  ***REMOVED*** Singleton instance
):
    return await backend.get_movies()
```

**Benefits**:

- 🚀 Performance optimization for heavy clients
- 🔄 Resource management (connection pooling)
- 🎯 Cache compatibility with method signatures

***REMOVED******REMOVED******REMOVED******REMOVED*** **2. Enhanced Service Client Factory** ⭐ **HIGH**

**Problem**: Basic HTTP clients don't support specialized client types or custom configurations.

**Solution**: Flexible client factory system:

```python
***REMOVED*** Proposed API
from fast_core.dependencies import ServiceClientFactory

factory = ServiceClientFactory()
factory.register_client_type("backend", BackendClient, singleton=True)
factory.register_client_type("auth", AuthClient, timeout=10)

***REMOVED*** Auto-generates dependencies
def get_backend_client() -> BackendClient:
    return factory.get_client("backend")
```

***REMOVED******REMOVED******REMOVED*** **Phase 2: Developer Experience** (Medium Priority)

***REMOVED******REMOVED******REMOVED******REMOVED*** **3. Domain-Specific Response Utilities** ⭐ **MEDIUM**

**Problem**: Services need domain-specific response wrappers beyond basic success/error responses.

**Solution**: Response builder system:

```python
***REMOVED*** Proposed API
from fast_core.responses import ResponseBuilder

movie_responses = ResponseBuilder("movies")
search_responses = ResponseBuilder("search")

***REMOVED*** Smart defaults based on domain
def get_movies():
    return movie_responses.list_response(
        items=movies,
        total=1000,
        page=1,
        per_page=20
    )
```

***REMOVED******REMOVED******REMOVED******REMOVED*** **4. Middleware Configuration Builder** ⭐ **COMPLETE**

**Problem**: All-or-nothing middleware approach in AppOptions lacks granular control.

**Solution**: Flexible middleware configuration:

```python
***REMOVED*** Current API
from fast_core.middleware import MiddlewareConfig

middleware = MiddlewareConfig()
middleware.cors(origins=["*"], credentials=True)
middleware.logging(level="INFO", exclude_paths=["/health"])
middleware.rate_limiting(default_limit="100/minute")
middleware.security_headers(hsts=True, csp="default-src 'self'")

app = create_app(middleware=middleware)
```

***REMOVED******REMOVED******REMOVED*** **Phase 3: Convenience Features** (Nice to Have)

***REMOVED******REMOVED******REMOVED******REMOVED*** **5. Configuration Auto-Discovery** ⭐ **LOW**

**Problem**: Manual configuration mapping between service configs and FastAPIConfig.

**Solution**: Annotation-based config discovery:

```python
***REMOVED*** Proposed API
from fast_core.config import fast_core_config, service_url, feature_flag

@fast_core_config
class MyServiceConfig:
    @service_url("backend")
    backend_api_url: str = "http://localhost:8000"

    @feature_flag("recommendations")
    enable_recommendations: bool = True

***REMOVED*** Auto-generates FastAPIConfig
config = auto_discover_config(MyServiceConfig())
```

***REMOVED******REMOVED******REMOVED******REMOVED*** **6. Enhanced Health Check Patterns** ⭐ **LOW**

**Problem**: Basic health checks without service-specific patterns.

**Solution**: Service-specific health check builders:

```python
***REMOVED*** Proposed API
from fast_core.monitoring import HealthCheckConfig

health = HealthCheckConfig()
health.add_database_check("main_db", connection_string)
health.add_service_check("backend", url, timeout=5)
health.add_cache_check("redis", redis_url)

***REMOVED*** Auto-generates /health endpoints with detailed status
```

***REMOVED******REMOVED******REMOVED*** **Implementation Status**

| **Enhancement**        | **Priority** | **Status**      | **Target Version** |
| ---------------------- | ------------ | --------------- | ------------------ |
| Singleton Dependencies | High         | ✅ **COMPLETE** | v0.2.0             |
| Service Client Factory | High         | ✅ **COMPLETE** | v0.2.0             |
| Response Utilities     | Medium       | ✅ **COMPLETE** | v0.2.0             |
| Middleware Builder     | Medium       | ✅ **COMPLETE** | v0.3.0             |
| Config Auto-Discovery  | Low          | 💡 Proposed     | v0.4.0             |
| Enhanced Health Checks | Low          | 💡 Proposed     | v0.4.0             |

***REMOVED******REMOVED******REMOVED*** **Integration Experience**

These enhancements are based on real-world experience from the **BFF API integration**, which achieved **90% Fast Core adoption** and identified these patterns as the most valuable for production services.

**Key Learnings**:

- ✅ Singleton patterns are critical for performance-sensitive services (**IMPLEMENTED**)
- ✅ Service client factories enable flexible service-to-service communication (**IMPLEMENTED**)
- ✅ Domain-specific response utilities reduce boilerplate significantly (**IMPLEMENTED**)
- ✅ Flexible middleware configuration is essential for different service needs (**IMPLEMENTED**)
- ✅ Auto-discovery reduces manual configuration mapping overhead

**Latest Achievements**:

- ✅ **Generic Response Patterns System** - Complete implementation with paginated, detail, search, collection, action, and error response patterns. Includes configurable behavior, rich metadata support, type safety, and production-ready integration with BFF API demo endpoints!

- ✅ **Middleware Configuration Builder** - Complete implementation with granular middleware control using builder pattern. Includes CORS, security headers, rate limiting, logging, and request processing middleware with full type safety and production-ready examples!

***REMOVED******REMOVED******REMOVED*** **Contributing to Enhancements**

1. **Review Enhancement Proposals**: Check the detailed specifications in each enhancement
2. **Implementation Guidelines**: Follow established patterns and maintain backward compatibility
3. **Testing Requirements**: Each enhancement must include comprehensive tests
4. **Documentation**: Update relevant README files and examples
5. **Integration Testing**: Validate with existing services (BFF API as reference)

***REMOVED******REMOVED*** Contributing

1. Follow the established patterns in existing modules
2. Add comprehensive tests for new functionality
3. Update documentation and README files
4. Ensure type annotations are complete
5. Follow the Next Watch coding standards
6. **Enhancement Contributions**: See the Enhancement Roadmap above for priority areas

***REMOVED******REMOVED*** License

This library is part of the Next Watch project and follows the project's licensing terms.

***REMOVED******REMOVED*** Changelog

***REMOVED******REMOVED******REMOVED*** v0.1.0

- Initial implementation with core modules
- Dependencies, security, errors, middleware, routing
- JWT authentication and rate limiting
- API versioning and pagination
- Health monitoring and metrics
- Integration with Next Watch libraries

***REMOVED******REMOVED******REMOVED*** v0.2.0

- **Enhanced Monitoring**: Comprehensive Prometheus metrics integration
- **Singleton Dependencies**: Performance-optimized service client patterns
- **Service Client Factory**: Flexible HTTP client management with custom configurations
- **Response Utilities**: Generic response patterns for consistent API responses

***REMOVED******REMOVED******REMOVED*** v0.3.0

- **Middleware Builder**: Granular middleware configuration with builder pattern
- **Metrics Middleware**: Automatic request/response metrics collection
- **Production Integration**: Full deployment across NextWatch services (BFF, Backend, Search, Recommendation, Auth APIs)
- **Performance Optimization**: Custom metric buckets and efficient data collection

***REMOVED******REMOVED*** Response Utilities (NEW!) 🎯

Fast Core now includes a powerful `ResponseBuilder` for creating consistent, well-structured API responses across all your services.

***REMOVED******REMOVED******REMOVED*** Key Features

- **Generic Response Patterns**: Paginated, detail, search, collection, action, and error responses
- **Configurable Behavior**: Customize response structure per service needs
- **Rich Metadata Support**: Include cache info, service details, performance metrics
- **Type Safety**: Full TypeScript-style type definitions with TypedDict
- **Framework Agnostic**: Works with any Python web framework

***REMOVED******REMOVED******REMOVED*** Quick Start

```python
from fast_core.responses import ResponseBuilder

***REMOVED*** Initialize with optional configuration
responses = ResponseBuilder(config={
    "pagination": {"default_limit": 20, "max_limit": 100},
    "detail": {"include_metadata": True}
})

***REMOVED*** Paginated responses
movies_response = responses.paginated(
    items=movies,
    page=1,
    limit=20,
    total=150,
    metadata={
        "filters_applied": {"genre": "action"},
        "cache_hit": True,
        "query_time_ms": 45
    }
)

***REMOVED*** Detail responses
movie_response = responses.detail(
    item=movie,
    related={
        "cast": cast_members,
        "trailers": trailers,
        "similar_movies": similar
    },
    context={
        "user_interactions": user_data,
        "personalized": True
    },
    metadata={
        "aggregated_from": ["backend-api", "recommendation-api"],
        "api_version": "v1"
    }
)

***REMOVED*** Search responses
search_response = responses.search(
    query="action movies",
    results=search_results,
    facets={"genre": {"values": [{"action": 15}]}},
    suggestions=["action films", "adventure movies"],
    metadata={"search_time_ms": 25}
)

***REMOVED*** Action responses (POST/PUT/DELETE)
action_response = responses.action(
    success=True,
    action="movie_added_to_watchlist",
    data={"movie_id": 123},
    message="Movie added successfully"
)

***REMOVED*** Error responses
error_response = responses.error(
    code="MOVIE_NOT_FOUND",
    message="The requested movie was not found",
    details=[{"field": "movie_id", "code": "INVALID"}],
    suggestions=["Check movie ID", "Browse popular movies"]
)
```

***REMOVED******REMOVED******REMOVED*** Response Patterns

***REMOVED******REMOVED******REMOVED******REMOVED*** 1. Paginated Response

```json
{
  "results": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  },
  "metadata": {
    "filters_applied": {...},
    "cache_hit": true
  }
}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 2. Detail Response

```json
{
  "data": {...},
  "related": {
    "cast": [...],
    "trailers": [...],
    "similar_movies": [...]
  },
  "context": {
    "user_interactions": {...},
    "personalized": true
  },
  "metadata": {
    "aggregated_from": ["backend-api"],
    "api_version": "v1"
  }
}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 3. Search Response

```json
{
  "query": "action movies",
  "results": [...],
  "facets": {
    "genre": {"values": [{"action": 15}]}
  },
  "suggestions": ["action films"],
  "metadata": {"search_time_ms": 25}
}
```

***REMOVED******REMOVED******REMOVED*** BFF API Integration

The ResponseBuilder is successfully integrated into the BFF API with demo endpoints:

```python
***REMOVED*** In BFF API routes
from fast_core.responses import ResponseBuilder

responses = ResponseBuilder(config={
    "pagination": {"default_limit": 20, "max_limit": 100},
    "detail": {"include_metadata": True}
})

@router.get("/movies/{movie_id}/response-builder-demo")
async def get_movie_demo(movie_id: int):
    """Demo endpoint showing ResponseBuilder detail pattern."""
    movie = await backend.get_movie(movie_id)
    cast = await backend.get_movie_cast(movie_id)
    similar = await recommendation_client.get_similar_movies(movie_id)

    return responses.detail(
        item=movie,
        related={"cast": cast, "similar_movies": similar},
        context={"user_interactions": user_data},
        metadata={
            "aggregated_from": ["backend-api", "recommendation-api"],
            "api_version": "v1"
        }
    )

@router.get("/movies/response-builder-demo")
async def get_movies_demo(page: int = 1, limit: int = 20):
    """Demo endpoint showing ResponseBuilder paginated pattern."""
    movies_data = await backend.get_movies(page=page, limit=limit)

    return responses.paginated(
        items=movies_data["results"],
        page=page,
        limit=limit,
        total=movies_data["total"],
        metadata={
            "service_info": {"aggregated_from": ["backend-api"]},
            "performance": {"cache_hit": False}
        }
    )
```

***REMOVED******REMOVED******REMOVED*** Configuration Options

```python
config = {
    "pagination": {
        "default_limit": 20,
        "max_limit": 100,
        "include_total_pages": True,
        "include_has_next_prev": True
    },
    "detail": {
        "include_timestamps": True,
        "include_metadata": True
    },
    "search": {
        "include_suggestions": True,
        "include_facets": True
    },
    "errors": {
        "include_suggestions": True,
        "include_details": True
    }
}

builder = ResponseBuilder(config=config)
```

***REMOVED******REMOVED******REMOVED*** Available Response Types

- **`PaginatedResponse`**: For paginated data with metadata
- **`DetailResponse`**: For single item details with related data
- **`CollectionResponse`**: For grouped collections of items
- **`SearchResponse`**: For search results with facets and suggestions
- **`ActionResponse`**: For POST/PUT/DELETE operation results
- **`ErrorResponse`**: For structured error information

***REMOVED******REMOVED******REMOVED*** Benefits

✅ **Consistency**: All APIs use the same response structure
✅ **Rich Metadata**: Include performance, cache, and service information
✅ **Type Safety**: Full type definitions for better IDE support
✅ **Flexibility**: Configurable behavior per service needs
✅ **Framework Agnostic**: Works with FastAPI, Flask, Django, etc.
✅ **Production Ready**: Used in BFF API with caching and authentication
