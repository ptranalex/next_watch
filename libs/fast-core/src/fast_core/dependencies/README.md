# Dependencies Module

The dependencies module provides a comprehensive set of dependency injection utilities for FastAPI applications. These dependencies standardize common patterns like authentication, database access, caching, and request handling across Next Watch services.

## Overview

This module contains dependency functions that can be injected into FastAPI route handlers to provide common functionality:

- **Common Dependencies**: Request metadata, pagination, search parameters
- **Authentication**: API key validation, user authentication, role-based authorization
- **Database**: Session management, transactions, read-only access
- **Cache**: Redis client, cache manager, cache service operations

## Usage

```python
from fastapi import FastAPI, Depends
from fast_core.dependencies import (
    get_current_user,
    get_db_session,
    get_cache_manager,
    get_pagination_params
)

app = FastAPI()

@app.get("/users")
async def list_users(
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    # Your route logic here
    pass
```

## Module Structure

### `common.py`

Basic request handling dependencies:

- `get_settings()`: Application settings/configuration
- `get_request_id()`: Unique request identifier for tracing
- `get_pagination_params()`: Standardized pagination parameters
- `get_search_params()`: Search query parameters

### `auth.py`

Authentication and authorization dependencies:

- `get_api_key()`: Extract and validate API key from headers
- `get_current_user()`: Get authenticated user from JWT token
- `require_roles()`: Factory for role-based authorization
- `require_permissions()`: Factory for permission-based authorization

**Example:**

```python
from fast_core.dependencies.auth import get_current_user, require_roles

@app.get("/admin/users")
async def admin_users(
    user: User = Depends(get_current_user),
    _: None = Depends(require_roles(["admin", "moderator"])),
):
    pass
```

### `database.py`

Database session and transaction management:

- `get_db_session()`: Standard database session
- `get_db_transaction()`: Auto-committing transaction session
- `get_readonly_db_session()`: Read-only database session
- `get_db_service()`: Database service with common operations

**Example:**

```python
from fast_core.dependencies.database import get_db_session, get_db_transaction

@app.post("/users")
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_transaction),  # Auto-commits
):
    # Database changes are automatically committed
    pass

@app.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_readonly_db_session),  # Read-only
):
    # Cannot modify database
    pass
```

### `cache.py`

Caching utilities and Redis integration:

- `get_cache_manager()`: Cache manager instance
- `get_redis_client()`: Direct Redis client access
- `get_cache_service()`: High-level cache service with CRUD operations

**Example:**

```python
from fast_core.dependencies.cache import get_cache_service

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    cache: CacheService = Depends(get_cache_service),
):
    # Try cache first
    cached_user = await cache.get(f"user:{user_id}")
    if cached_user:
        return cached_user

    # Fetch from database and cache
    user = await fetch_user_from_db(user_id)
    await cache.set(f"user:{user_id}", user, ttl=300)
    return user
```

## Configuration

Dependencies rely on proper configuration in your FastAPI application:

```python
from fast_core import create_app, FastAPIConfig

config = FastAPIConfig(
    database_url="postgresql://...",
    redis_url="redis://localhost:6379",
    jwt_secret_key="your-secret-key",
)

app = create_app(config=config)
```

## Error Handling

All dependencies include proper error handling:

- **Authentication errors**: Return 401 Unauthorized
- **Authorization errors**: Return 403 Forbidden
- **Database errors**: Return 500 Internal Server Error with proper logging
- **Cache errors**: Graceful fallback, don't fail requests

## Integration with Next Watch Services

These dependencies are designed to work seamlessly with:

- **Config Library**: Automatic configuration loading
- **Cache Library**: Redis and memory caching
- **CLI Library**: Command-line utilities and logging
- **Movie Storage**: Database models and operations

## Best Practices

1. **Use appropriate session types**:

   - `get_db_session()` for mixed read/write operations
   - `get_db_transaction()` for operations that must be atomic
   - `get_readonly_db_session()` for read-only operations

2. **Cache strategically**:

   - Use `get_cache_service()` for high-level operations
   - Use `get_redis_client()` for complex Redis operations
   - Set appropriate TTL values

3. **Authentication patterns**:

   - Use `get_current_user()` for user-specific operations
   - Combine with `require_roles()` for authorization
   - Use `get_api_key()` for service-to-service communication

4. **Request tracing**:
   - Always include `get_request_id()` for debugging
   - Use request ID in logs and error messages

## Testing

Dependencies can be easily overridden in tests:

```python
from fastapi.testclient import TestClient
from fast_core.dependencies import get_current_user

def override_get_current_user():
    return User(id=1, username="testuser")

app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(app)
```
