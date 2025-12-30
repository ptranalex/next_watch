# Routing Module

The routing module provides advanced routing utilities for FastAPI applications, including API versioning, pagination, and base router classes. These components help build scalable and maintainable APIs across Next Watch services.

## Overview

This module contains:

- **Base Router**: Foundation router class with common functionality
- **Pagination**: Comprehensive pagination utilities and helpers
- **Versioning**: Multi-strategy API versioning support

## Module Structure

### `base.py` - Base Router

Provides a foundation router class with common patterns and utilities.

#### Basic Usage

```python
from fast_core.routing.base import BaseRouter
from fastapi import FastAPI

app = FastAPI()

# Create a base router
router = BaseRouter(prefix="/api/v1", tags=["users"])

@router.get("/users")
async def list_users():
    return {"users": []}

app.include_router(router)
```

#### Features

- Consistent router configuration
- Common response patterns
- Error handling integration
- Standardized route registration

### `pagination.py` - Pagination Utilities

Comprehensive pagination system with parameters, metadata, and response formatting.

#### Key Components

- `PaginationParams`: Query parameters for pagination
- `PaginationMeta`: Metadata about pagination state
- `PaginatedResult`: Complete paginated response
- `Paginator`: Pagination logic handler

#### Basic Usage

```python
from fastapi import FastAPI, Depends
from fast_core.routing.pagination import (
    get_pagination_params,
    paginate_results,
    PaginationParams
)

app = FastAPI()

@app.get("/users")
async def list_users(
    pagination: PaginationParams = Depends(get_pagination_params)
):
    # Get total count
    total_users = await count_users()

    # Get paginated data
    users = await get_users(
        offset=pagination.offset,
        limit=pagination.limit
    )

    # Return paginated response
    return paginate_results(
        data=users,
        pagination=pagination,
        total_count=total_users
    )
```

#### Pagination Parameters

```python
class PaginationParams:
    page: int = 1          # Page number (1-based)
    per_page: int = 20     # Items per page
    offset: int            # Calculated offset
    limit: int             # Calculated limit
```

#### Query Parameters

- `?page=2&per_page=50` - Page 2 with 50 items per page
- `?page=1` - First page with default per_page (20)
- `?per_page=100` - First page with 100 items per page

#### Response Format

```json
{
  "data": [
    { "id": 1, "name": "User 1" },
    { "id": 2, "name": "User 2" }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 5,
    "total_count": 100,
    "has_next": true,
    "has_previous": false,
    "next_page": 2,
    "previous_page": null
  }
}
```

#### Advanced Usage

```python
from fast_core.routing.pagination import Paginator

# Custom pagination logic
paginator = Paginator(
    page=2,
    per_page=50,
    total_count=1000
)

# Get pagination metadata
meta = paginator.get_meta()
print(f"Page {meta.page} of {meta.total_pages}")

# Check pagination state
if paginator.has_next():
    print(f"Next page: {paginator.next_page}")
```

### `versioning.py` - API Versioning

Multi-strategy API versioning with flexible configuration options.

#### Versioning Strategies

1. **URL Path**: `/api/v1/users`, `/api/v2/users`
2. **Header**: `X-API-Version: v1`
3. **Query Parameter**: `?version=v1`
4. **Accept Header**: `Accept: application/vnd.api+json;version=1`

#### Basic Usage

```python
from fastapi import FastAPI, Depends
from fast_core.routing.versioning import (
    VersionedRouter,
    version_dependency,
    APIVersion
)

app = FastAPI()

# Create versioned router
router = VersionedRouter(
    prefix="/api",
    strategy="url_path"  # or "header", "query", "accept"
)

@router.get("/users", version="v1")
async def list_users_v1():
    return {"users": [], "version": "v1"}

@router.get("/users", version="v2")
async def list_users_v2():
    return {"users": [], "version": "v2", "enhanced": True}

app.include_router(router)
```

#### URL Path Versioning

```python
from fast_core.routing.versioning import VersionedRouter

# URL path strategy
router = VersionedRouter(
    prefix="/api",
    strategy="url_path"
)

# Routes become:
# GET /api/v1/users
# GET /api/v2/users
```

#### Header Versioning

```python
# Header strategy
router = VersionedRouter(
    prefix="/api",
    strategy="header",
    header_name="X-API-Version"
)

# Client sends: X-API-Version: v1
# Routes remain: GET /api/users
```

#### Query Parameter Versioning

```python
# Query parameter strategy
router = VersionedRouter(
    prefix="/api",
    strategy="query",
    query_param="version"
)

# Client sends: GET /api/users?version=v1
```

#### Accept Header Versioning

```python
# Accept header strategy
router = VersionedRouter(
    prefix="/api",
    strategy="accept",
    media_type="application/vnd.api+json"
)

# Client sends: Accept: application/vnd.api+json;version=1
```

#### Version Dependencies

```python
from fast_core.routing.versioning import version_dependency

@app.get("/users")
async def list_users(version: APIVersion = Depends(version_dependency)):
    if version.major >= 2:
        return {"users": [], "enhanced": True}
    return {"users": []}
```

#### Version-Specific Logic

```python
from fast_core.routing.versioning import APIVersion

def handle_user_request(version: APIVersion, user_data: dict):
    if version >= APIVersion.parse("v2.0"):
        # Enhanced v2 logic
        return enhance_user_data(user_data)
    elif version >= APIVersion.parse("v1.5"):
        # v1.5 logic
        return add_metadata(user_data)
    else:
        # Basic v1 logic
        return user_data
```

## Complete Integration Example

```python
from fastapi import FastAPI, Depends
from fast_core.routing import (
    BaseRouter,
    get_pagination_params,
    paginate_results,
    VersionedRouter,
    PaginationParams
)

app = FastAPI()

# Create versioned router with pagination
router = VersionedRouter(
    prefix="/api",
    strategy="url_path",
    tags=["users"]
)

@router.get("/users", version="v1")
async def list_users_v1(
    pagination: PaginationParams = Depends(get_pagination_params)
):
    # Get data with pagination
    users = await get_users_from_db(
        offset=pagination.offset,
        limit=pagination.limit
    )
    total_count = await count_users()

    # Return paginated response
    return paginate_results(
        data=users,
        pagination=pagination,
        total_count=total_count
    )

@router.get("/users", version="v2")
async def list_users_v2(
    pagination: PaginationParams = Depends(get_pagination_params)
):
    # Enhanced v2 with additional fields
    users = await get_enhanced_users_from_db(
        offset=pagination.offset,
        limit=pagination.limit
    )
    total_count = await count_users()

    return paginate_results(
        data=users,
        pagination=pagination,
        total_count=total_count
    )

app.include_router(router)
```

## Configuration

Routing components can be configured through environment variables:

```bash
# Pagination Configuration
PAGINATION_DEFAULT_PER_PAGE=20
PAGINATION_MAX_PER_PAGE=100
PAGINATION_ALLOW_ZERO_RESULTS=true

# Versioning Configuration
API_VERSION_STRATEGY=url_path
API_VERSION_HEADER_NAME=X-API-Version
API_VERSION_QUERY_PARAM=version
API_VERSION_MEDIA_TYPE=application/vnd.api+json
API_DEFAULT_VERSION=v1
```

## Best Practices

### Pagination

1. **Reasonable Defaults**: Use sensible default page sizes (20-50 items)
2. **Maximum Limits**: Prevent large page sizes that could impact performance
3. **Consistent Format**: Always use the same pagination response structure
4. **Total Count**: Include total count for UI pagination controls
5. **Cursor Pagination**: Consider cursor-based pagination for large datasets

### Versioning

1. **Semantic Versioning**: Use semantic version numbers (v1.0, v1.1, v2.0)
2. **Backward Compatibility**: Maintain compatibility within major versions
3. **Deprecation Strategy**: Clearly communicate version deprecation timelines
4. **Default Version**: Always specify a default version for unversioned requests
5. **Documentation**: Document version differences clearly

### Routing

1. **Consistent Prefixes**: Use consistent URL prefixes across services
2. **Resource Naming**: Use plural nouns for resource endpoints
3. **HTTP Methods**: Follow REST conventions for HTTP methods
4. **Error Handling**: Integrate with the errors module for consistent responses

## Testing

### Pagination Testing

```python
from fastapi.testclient import TestClient

def test_pagination_default(client: TestClient):
    response = client.get("/api/v1/users")
    data = response.json()

    assert response.status_code == 200
    assert "data" in data
    assert "pagination" in data
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 20

def test_pagination_custom(client: TestClient):
    response = client.get("/api/v1/users?page=2&per_page=50")
    data = response.json()

    assert data["pagination"]["page"] == 2
    assert data["pagination"]["per_page"] == 50
```

### Versioning Testing

```python
def test_url_path_versioning(client: TestClient):
    # Test v1
    response_v1 = client.get("/api/v1/users")
    assert response_v1.status_code == 200

    # Test v2
    response_v2 = client.get("/api/v2/users")
    assert response_v2.status_code == 200

def test_header_versioning(client: TestClient):
    response = client.get("/api/users", headers={"X-API-Version": "v1"})
    assert response.status_code == 200
```

## Performance Considerations

### Pagination

1. **Database Indexes**: Ensure proper indexing for pagination queries
2. **Count Queries**: Consider caching total counts for large datasets
3. **Offset Limitations**: Use cursor pagination for very large datasets
4. **Memory Usage**: Be mindful of memory usage with large page sizes

### Versioning

1. **Route Resolution**: URL path versioning has minimal overhead
2. **Header Parsing**: Header-based versioning adds slight parsing overhead
3. **Code Duplication**: Minimize code duplication between versions
4. **Caching**: Version-specific responses can be cached separately

## Integration with Next Watch Services

The routing module integrates with:

- **Error Handling**: Consistent error responses across versions
- **Dependencies**: Authentication and authorization per version
- **Monitoring**: Request metrics by version and pagination parameters
- **Documentation**: OpenAPI documentation with version-specific schemas

## Migration Guide

### Adding Pagination

```python
# Before
@app.get("/users")
async def list_users():
    users = await get_all_users()
    return {"users": users}

# After
@app.get("/users")
async def list_users(
    pagination: PaginationParams = Depends(get_pagination_params)
):
    users = await get_users_paginated(
        offset=pagination.offset,
        limit=pagination.limit
    )
    total_count = await count_users()

    return paginate_results(
        data=users,
        pagination=pagination,
        total_count=total_count
    )
```

### Adding Versioning

```python
# Before
router = APIRouter(prefix="/api")

@router.get("/users")
async def list_users():
    return {"users": []}

# After
router = VersionedRouter(prefix="/api", strategy="url_path")

@router.get("/users", version="v1")
async def list_users_v1():
    return {"users": []}

@router.get("/users", version="v2")
async def list_users_v2():
    return {"users": [], "enhanced": True}
```
