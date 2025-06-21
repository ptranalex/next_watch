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
- **Monitoring**: Health checks and system monitoring

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

Essential middleware components:

- **CORS**: Cross-Origin Resource Sharing configuration
- **Logging**: Request/response logging with timing and context
- **Security**: Security headers, rate limiting, and trusted hosts

***REMOVED******REMOVED******REMOVED*** 🛣️ [Routing](src/fast_core/routing/README.md)

Advanced routing utilities:

- **Pagination**: Comprehensive pagination with metadata and response formatting
- **Versioning**: Multi-strategy API versioning (URL, header, query, accept)
- **Base Router**: Foundation router class with common functionality

***REMOVED******REMOVED*** Features

***REMOVED******REMOVED******REMOVED*** Application Factory

```python
from fast_core import create_app, AppOptions

***REMOVED*** Basic app creation
app = create_app()

***REMOVED*** Advanced configuration
app = create_app(
    config=FastAPIConfig(
        title="My API",
        version="1.0.0",
        debug=False
    ),
    options=AppOptions(
        enable_cors=True,
        enable_security=True,
        enable_monitoring=True
    )
)
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

***REMOVED*** Logging
LOG_LEVEL=INFO
```

***REMOVED******REMOVED*** Integration with Next Watch Services

Fast Core is designed to work seamlessly with other Next Watch libraries:

- **Config Library**: Environment-based configuration loading
- **Cache Library**: Redis and memory caching integration
- **CLI Library**: Command-line utilities and structured logging
- **Movie Storage**: Database models and operations

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

***REMOVED******REMOVED*** Contributing

1. Follow the established patterns in existing modules
2. Add comprehensive tests for new functionality
3. Update documentation and README files
4. Ensure type annotations are complete
5. Follow the Next Watch coding standards

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
