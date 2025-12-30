# BFF API Routes

This module contains all the API endpoints (routes) for the BFF API service, implementing a **fast-core integrated** architecture with versioned, resource-based organization.

## Structure

The routes module follows a versioned, resource-based organization integrated with fast-core:

```
bff_api/routes/
│
├── __init__.py           # Package initialization
├── api_v1.py            # API v1 router aggregation (/bff/v1)
├── meta.py              # Meta endpoints (/, /debug)
├── health.py            # Health check endpoints (/health/*)
├── demo_fast_core.py    # Fast-core integration demo routes
├── README.md            # This documentation
│
└── v1/                  # API v1 routes by resource
    ├── __init__.py      # v1 package initialization
    ├── actors.py        # Actor/person endpoints
    ├── auth.py          # Authentication endpoints
    ├── genres.py        # Genre-related endpoints
    ├── home.py          # Home screen aggregation
    ├── liked.py         # User liked movies
    ├── movies.py        # Movie-related endpoints
    ├── search.py        # Search endpoints
    ├── sidebar.py       # Sidebar content
    ├── top.py           # Top movies with filtering
    ├── user_interactions.py  # User interaction management
    ├── watched.py       # User watched movies
    └── watchlist.py     # User watchlist management
```

## Fast-Core Integration

Routes are fully integrated with fast-core for standardized patterns:

### **Application Registration**

```python
# In bff_api/core/app_fast_core.py
from bff_api.routes.api_v1 import api_v1_router
from bff_api.routes.health import router as health_router
from bff_api.routes.meta import router as meta_router

routers = [
    meta_router,           # Meta endpoints
    health_router,         # Health checks
    api_v1_router,         # Main BFF API
    demo_router,           # Fast-core demo
]

app = create_app(
    settings=fast_core_config,
    routers=routers,       # Fast-core handles registration
    # ... other options
)
```

### **Dependency Injection**

All routes use fast-core and BFF hybrid dependencies:

```python
from bff_api.dependencies import get_backend_client, get_current_user_id
from fastapi import Depends

async def get_movies(
    backend: BackendClient = Depends(get_backend_client),
    user_id: Optional[int] = Depends(get_optional_user_id),
):
    # Fast-core handles middleware, logging, error handling automatically
    movies = await backend.get_movies(user_id=user_id)
    return movies
```

## API Versioning & Prefixes

### **Current API Structure**

- **BFF API v1**: `/bff/v1/*` - Main BFF endpoints
- **Meta**: `/` - Root and debug endpoints
- **Health**: `/health/*` - Health monitoring
- **Demo**: `/demo/*` - Fast-core integration examples

### **BFF v1 Endpoints**

The main BFF API uses the `/bff/v1/` prefix:

```bash
# Home screen aggregation
GET /bff/v1/home

# Movie operations
GET /bff/v1/movies
GET /bff/v1/movies/{movie_id}
POST /bff/v1/movies/{movie_id}/rate

# User-specific content
GET /bff/v1/watchlist
GET /bff/v1/watched
GET /bff/v1/liked

# Search and discovery
GET /bff/v1/search
GET /bff/v1/top
GET /bff/v1/genres

# User interactions
POST /bff/v1/user_interactions/like
POST /bff/v1/user_interactions/watch
```

## Route Categories

### **Content Aggregation Routes**

- **`home.py`**: Home screen data aggregation (featured, popular, recent, genres)
- **`sidebar.py`**: Sidebar content with caching
- **`top.py`**: Top movies with complex filtering and user interactions

### **Movie & Content Routes**

- **`movies.py`**: Movie details, operations, and metadata
- **`genres.py`**: Genre-based content discovery
- **`actors.py`**: Actor/person information and filmography

### **User-Specific Routes**

- **`watchlist.py`**: User watchlist management with bulk operations
- **`watched.py`**: User watched movies with filtering and sorting
- **`liked.py`**: User liked movies with advanced filtering
- **`user_interactions.py`**: Like, watch, rate, and other user actions

### **Discovery Routes**

- **`search.py`**: Movie search with suggestions and filtering
- **`auth.py`**: Authentication and user management

### **System Routes**

- **`meta.py`**: Root endpoint, debug information
- **`health.py`**: Comprehensive health monitoring
- **`demo_fast_core.py`**: Fast-core integration examples

## Route Implementation Patterns

### **Standard Route Structure**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from bff_api.dependencies import get_backend_client, get_current_user_id
from bff_api.services.clients.facade import BackendClient

router = APIRouter()

async def _handle_backend_error(error: Exception, operation: str) -> None:
    """Standard error handling for backend operations."""
    # Centralized error handling logic

@router.get("/resource")
async def get_resource(
    # Query parameters with validation
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),

    # Dependency injection
    backend: BackendClient = Depends(get_backend_client),
    user_id: Optional[int] = Depends(get_optional_user_id),
):
    """
    Comprehensive endpoint documentation.

    Args:
        page: Page number for pagination
        limit: Number of items per page
        backend: Backend client dependency
        user_id: Optional authenticated user ID

    Returns:
        Resource data with pagination
    """
    try:
        result = await backend.get_resource(
            page=page,
            limit=limit,
            user_id=user_id
        )
        return result
    except Exception as e:
        await _handle_backend_error(e, "get_resource")
```

### **Authentication Patterns**

```python
# Required authentication
async def protected_endpoint(
    user_id: int = Depends(get_current_user_id),
):
    # User must be authenticated

# Optional authentication
async def public_endpoint(
    user_id: Optional[int] = Depends(get_optional_user_id),
):
    # Personalized if authenticated, public otherwise

# Authentication with token access
async def proxy_endpoint(
    user_data: Tuple[int, str] = Depends(get_current_user_id_and_token),
):
    user_id, token = user_data
    # Can forward token to downstream services
```

### **Error Handling**

All routes use consistent error handling:

```python
async def _handle_backend_error(error: Exception, operation: str) -> None:
    """Handle backend service errors consistently."""
    if isinstance(error, httpx.HTTPStatusError):
        if error.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Resource not found")
        elif error.response.status_code >= 500:
            raise HTTPException(status_code=503, detail="Backend service unavailable")

    logger.error(f"Backend error in {operation}", error=str(error))
    raise HTTPException(status_code=500, detail="Internal server error")
```

## Fast-Core Features

### **Automatic Middleware**

Fast-core automatically provides:

- **Logging**: Request/response logging with request IDs
- **CORS**: Configured CORS for frontend applications
- **Error Handling**: Global exception handlers
- **Health Checks**: Automatic health monitoring

### **Service Dependencies**

```python
# Available service client dependencies
from bff_api.dependencies import (
    get_backend_client,        # Singleton BackendClient (BFF-specific)
    get_auth_client,          # HTTP client for auth service
    get_recommendation_client, # HTTP client for recommendation service
    get_ml_client,            # HTTP client for ML service
)
```

### **Health Monitoring**

Fast-core provides comprehensive health endpoints:

- `/health` - Overall service health
- `/health/ready` - Readiness probe for load balancers
- `/health/live` - Liveness probe for container orchestration

## Design Principles

### **Fast-Core Integration**

1. **Standardized Patterns**: Leverage fast-core for common functionality
2. **Hybrid Dependencies**: Use fast-core where appropriate, BFF-specific where needed
3. **Performance Optimization**: Singleton backend client for cache compatibility
4. **Consistent Error Handling**: Standardized error responses across all routes

### **BFF-Specific Patterns**

1. **Data Aggregation**: Combine data from multiple backend services
2. **Cache Integration**: Leverage caching for performance optimization
3. **User Context**: Personalize responses based on authentication
4. **Frontend Optimization**: Structure responses for frontend consumption

### **REST Conventions**

- Collection endpoints: `/resource` (e.g., `/movies`)
- Item endpoints: `/resource/{id}` (e.g., `/movies/123`)
- Actions: `/resource/{id}/action` (e.g., `/movies/123/rate`)
- User-specific: `/user-resource` (e.g., `/watchlist`)

## Testing Patterns

### **Route Testing**

```python
from fastapi.testclient import TestClient
from bff_api.core import create_app

def test_movie_endpoint():
    app = create_app()
    client = TestClient(app)

    response = client.get("/bff/v1/movies/1")
    assert response.status_code == 200
    assert "title" in response.json()

def test_authenticated_endpoint():
    app = create_app()
    client = TestClient(app)

    headers = {"Authorization": "Bearer valid.token"}
    response = client.get("/bff/v1/watchlist", headers=headers)
    assert response.status_code == 200
```

### **Dependency Mocking**

```python
from unittest.mock import Mock
from bff_api.dependencies import get_backend_client

def test_with_mocked_backend(app):
    mock_backend = Mock()
    mock_backend.get_movies.return_value = {"movies": []}

    app.dependency_overrides[get_backend_client] = lambda: mock_backend

    client = TestClient(app)
    response = client.get("/bff/v1/movies")
    assert response.status_code == 200
```

## Extension Guidelines

### **Adding New Routes**

1. **Identify Resource Category**: Determine if it fits existing route files
2. **Create Route File**: Add new file in `v1/` directory if needed
3. **Define Router**: Create APIRouter with appropriate tags
4. **Implement Handlers**: Follow established patterns and conventions
5. **Register Router**: Add to `api_v1.py` router aggregation
6. **Add Tests**: Implement comprehensive route testing

### **Route File Template**

```python
"""Resource-specific routes for BFF API v1."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from bff_api.dependencies import get_backend_client, get_optional_user_id
from bff_api.services.clients.facade import BackendClient

router = APIRouter()

async def _handle_backend_error(error: Exception, operation: str) -> None:
    """Handle backend errors for resource operations."""
    # Standard error handling implementation

@router.get("/")
async def get_resources(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    backend: BackendClient = Depends(get_backend_client),
    user_id: Optional[int] = Depends(get_optional_user_id),
):
    """Get paginated list of resources."""
    try:
        return await backend.get_resources(page=page, limit=limit, user_id=user_id)
    except Exception as e:
        await _handle_backend_error(e, "get_resources")
```

## Performance Considerations

### **Caching Strategy**

- **Backend Client**: Singleton pattern for connection reuse
- **Method-Level Caching**: Cache decorators on BackendClient methods
- **Response Caching**: Fast-core middleware for response caching

### **Optimization Patterns**

- **Bulk Operations**: Batch requests where possible
- **Parallel Requests**: Use asyncio for concurrent service calls
- **Efficient Queries**: Optimize backend API calls
- **Pagination**: Implement consistent pagination across endpoints

---

This routes system provides a robust, fast-core integrated foundation for the BFF API, combining standardized patterns with BFF-specific optimizations for optimal performance and maintainability.
