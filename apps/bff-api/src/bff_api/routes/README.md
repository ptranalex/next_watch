***REMOVED*** BFF API Routes

This module contains all the API endpoints (routes) for the BFF API service, organized by version and resource type.

***REMOVED******REMOVED*** Structure

The routes module follows a versioned, resource-based organization:

```
bff_api/routes/
│
├── __init__.py        ***REMOVED*** Package initialization
├── api_v1.py          ***REMOVED*** API v1 router aggregation
│
└── v1/                ***REMOVED*** API v1 routes by resource
    ├── __init__.py    ***REMOVED*** v1 package initialization
    ├── auth.py        ***REMOVED*** Authentication endpoints
    ├── movies.py      ***REMOVED*** Movie-related endpoints
    ├── shows.py       ***REMOVED*** TV show-related endpoints
    ├── people.py      ***REMOVED*** Person/actor-related endpoints
    ├── search.py      ***REMOVED*** Search endpoints
    ├── users.py       ***REMOVED*** User profile endpoints
    └── watchlist.py   ***REMOVED*** User watchlist endpoints
```

***REMOVED******REMOVED*** API Versioning

The API uses URL-based versioning with the `/api/v{n}/` prefix. Each version has its own package:

- Current version: `/api/v1/`
- Future versions will be added as `/api/v2/`, etc.

This enables the API to evolve while maintaining backward compatibility.

***REMOVED******REMOVED*** Route Registration

Routes are registered in a hierarchical manner:

1. Individual resource routers are defined in files within the `v1/` directory
2. These routers are collected in `api_v1.py` into a single router
3. The version router is mounted in the FastAPI app in `main.py`

Example:

```python
***REMOVED*** In v1/movies.py
router = APIRouter(prefix="/movies", tags=["movies"])

@router.get("/{movie_id}")
async def get_movie(movie_id: int):
    """Get movie details."""
    ...

***REMOVED*** In api_v1.py
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(movies.router)
api_v1_router.include_router(shows.router)
***REMOVED*** ... other resource routers

***REMOVED*** In main.py
app = FastAPI()
app.include_router(api_v1_router)
```

***REMOVED******REMOVED*** Route Documentation

Each endpoint is documented using FastAPI's built-in support for OpenAPI:

- Comprehensive docstrings
- Parameter descriptions
- Response models
- Status codes
- Tags for grouping in the documentation

Example:

```python
@router.get(
    "/{movie_id}",
    response_model=MovieDetails,
    responses={
        404: {"description": "Movie not found"},
        500: {"description": "Server error"},
    },
    summary="Get movie details",
    description="Returns detailed information about a specific movie.",
)
async def get_movie(
    movie_id: int = Path(..., description="The ID of the movie to retrieve"),
    backend_client: BackendClient = Depends(get_backend_client),
) -> MovieDetails:
    """Get detailed information about a movie.

    Args:
        movie_id: The unique identifier of the movie
        backend_client: Injected backend client service

    Returns:
        MovieDetails object with full movie information

    Raises:
        HTTPException: If movie not found or server error
    """
    ...
```

***REMOVED******REMOVED*** Resource Naming Conventions

Routes follow REST conventions:

- Collection endpoints: `/resource` (e.g., `/movies`)
- Item endpoints: `/resource/{id}` (e.g., `/movies/123`)
- Sub-resource collections: `/resource/{id}/subresource` (e.g., `/movies/123/reviews`)
- Sub-resource items: `/resource/{id}/subresource/{subid}` (e.g., `/movies/123/reviews/456`)
- Actions: `/resource/{id}/action` (e.g., `/movies/123/rate`)

***REMOVED******REMOVED*** Design Principles

1. **Resource-Oriented**: Routes are organized around resources, not actions
2. **Consistent Structure**: Similar resources have similar endpoint structures
3. **Appropriate Methods**: HTTP methods reflect the intent (GET, POST, PUT, DELETE)
4. **Dependency Injection**: Services are injected via FastAPI dependencies
5. **Proper Status Codes**: Responses use appropriate HTTP status codes
6. **Well-Documented**: All endpoints have comprehensive documentation

***REMOVED******REMOVED*** Extension Guidelines

When adding new routes:

1. Identify the appropriate resource category
2. Create a new file in the `v1/` directory if needed
3. Define an `APIRouter` with the appropriate prefix and tags
4. Implement the route handlers following conventions
5. Register the router in `api_v1.py`
6. Add appropriate tests for the new endpoints

***REMOVED******REMOVED*** Best Practices

- Keep route handlers thin, delegating business logic to services
- Use response models to enforce response structure
- Implement comprehensive input validation
- Return appropriate status codes for different scenarios
- Use path parameters for resource identifiers
- Use query parameters for filtering and pagination
- Use request bodies for complex input data
- Implement proper error handling with clear error messages
