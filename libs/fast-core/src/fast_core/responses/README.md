***REMOVED*** Response Utilities

The Fast Core Response Utilities provide a powerful `ResponseBuilder` for creating consistent, well-structured API responses across all your services.

***REMOVED******REMOVED*** Features

- **Generic Response Patterns**: Paginated, detail, search, collection, action, and error responses
- **Configurable Behavior**: Customize response structure per service needs
- **Rich Metadata Support**: Include cache info, service details, performance metrics
- **Type Safety**: Full TypeScript-style type definitions with TypedDict
- **Framework Agnostic**: Works with any Python web framework

***REMOVED******REMOVED*** Quick Start

```python
from fast_core.responses import ResponseBuilder

***REMOVED*** Initialize with optional configuration
responses = ResponseBuilder(config={
    "pagination": {"default_limit": 20, "max_limit": 100},
    "detail": {"include_metadata": True}
})
```

***REMOVED******REMOVED*** Response Patterns

***REMOVED******REMOVED******REMOVED*** 1. Paginated Response

Perfect for list endpoints with pagination:

```python
***REMOVED*** Usage
response = responses.paginated(
    items=movies,
    page=1,
    limit=20,
    total=150,
    metadata={
        "filters_applied": {"genre": "action", "year": 2023},
        "cache_hit": True,
        "query_time_ms": 45
    }
)

***REMOVED*** Output structure
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
        "filters_applied": {"genre": "action", "year": 2023},
        "cache_hit": true,
        "query_time_ms": 45
    }
}
```

***REMOVED******REMOVED******REMOVED*** 2. Detail Response

Perfect for single item endpoints with related data:

```python
***REMOVED*** Usage
response = responses.detail(
    item=movie,
    related={
        "cast": cast_members,
        "trailers": trailers,
        "similar_movies": similar_movies
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

***REMOVED*** Output structure
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
        "aggregated_from": ["backend-api", "recommendation-api"],
        "api_version": "v1"
    }
}
```

***REMOVED******REMOVED******REMOVED*** 3. Search Response

Perfect for search endpoints with facets and suggestions:

```python
***REMOVED*** Usage
response = responses.search(
    query="action movies",
    results=search_results,
    facets={
        "genre": {"name": "Genre", "values": [{"action": 15}, {"drama": 8}]},
        "year": {"name": "Year", "values": [{"2023": 5}, {"2022": 10}]}
    },
    suggestions=["action films", "adventure movies"],
    metadata={"search_time_ms": 25, "total_indexed": 10000}
)

***REMOVED*** Output structure
{
    "query": "action movies",
    "results": [...],
    "facets": {
        "genre": {"name": "Genre", "values": [{"action": 15}, {"drama": 8}]},
        "year": {"name": "Year", "values": [{"2023": 5}, {"2022": 10}]}
    },
    "suggestions": ["action films", "adventure movies"],
    "metadata": {"search_time_ms": 25, "total_indexed": 10000}
}
```

***REMOVED******REMOVED******REMOVED*** 4. Collection Response

Perfect for grouped data endpoints:

```python
***REMOVED*** Usage
response = responses.collection(
    groups={
        "popular": popular_movies,
        "trending": trending_movies,
        "recommended": recommended_movies
    },
    metadata={
        "collection_types": ["popular", "trending", "recommended"],
        "total_movies": 150,
        "personalized": True
    }
)

***REMOVED*** Output structure
{
    "collections": {
        "popular": [...],
        "trending": [...],
        "recommended": [...]
    },
    "metadata": {
        "collection_types": ["popular", "trending", "recommended"],
        "total_movies": 150,
        "personalized": true
    }
}
```

***REMOVED******REMOVED******REMOVED*** 5. Action Response

Perfect for POST/PUT/DELETE operations:

```python
***REMOVED*** Success
response = responses.action(
    success=True,
    action="movie_added_to_watchlist",
    data={"movie_id": 123, "watchlist_id": 456},
    message="Movie successfully added to your watchlist"
)

***REMOVED*** Failure
response = responses.action(
    success=False,
    action="movie_removal_failed",
    message="Failed to remove movie from watchlist",
    metadata={"error_code": "MOVIE_NOT_IN_WATCHLIST"}
)

***REMOVED*** Output structure
{
    "success": true,
    "action": "movie_added_to_watchlist",
    "data": {"movie_id": 123, "watchlist_id": 456},
    "message": "Movie successfully added to your watchlist"
}
```

***REMOVED******REMOVED******REMOVED*** 6. Error Response

Perfect for structured error handling:

```python
***REMOVED*** Usage
response = responses.error(
    code="MOVIE_NOT_FOUND",
    message="The requested movie could not be found",
    details=[
        {
            "field": "movie_id",
            "code": "INVALID_ID",
            "message": "Movie ID must be a positive integer",
            "value": -1
        }
    ],
    suggestions=[
        "Check the movie ID is correct",
        "Browse popular movies instead",
        "Use the search feature to find movies"
    ],
    metadata={
        "request_id": "req_123456",
        "api_version": "v1"
    }
)

***REMOVED*** Output structure
{
    "error": {
        "code": "MOVIE_NOT_FOUND",
        "message": "The requested movie could not be found",
        "details": [
            {
                "field": "movie_id",
                "code": "INVALID_ID",
                "message": "Movie ID must be a positive integer",
                "value": -1
            }
        ],
        "suggestions": [
            "Check the movie ID is correct",
            "Browse popular movies instead",
            "Use the search feature to find movies"
        ]
    },
    "metadata": {
        "request_id": "req_123456",
        "api_version": "v1"
    }
}
```

***REMOVED******REMOVED*** Configuration

Customize the ResponseBuilder behavior with configuration:

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

***REMOVED*** Override configuration per call
response = builder.paginated(
    items=movies,
    page=1,
    limit=20,
    total=100,
    config_override={"include_total_pages": False}
)
```

***REMOVED******REMOVED*** FastAPI Integration

***REMOVED******REMOVED******REMOVED*** Basic Integration

```python
from fastapi import APIRouter, Depends
from fast_core.responses import ResponseBuilder

router = APIRouter()
responses = ResponseBuilder()

@router.get("/movies")
async def get_movies(page: int = 1, limit: int = 20):
    ***REMOVED*** Fetch data
    movies_data = await fetch_movies(page=page, limit=limit)

    ***REMOVED*** Return structured response
    return responses.paginated(
        items=movies_data["results"],
        page=page,
        limit=limit,
        total=movies_data["total"],
        metadata={
            "service": "movie-api",
            "cache_hit": False
        }
    )

@router.get("/movies/{movie_id}")
async def get_movie(movie_id: int):
    ***REMOVED*** Fetch movie and related data
    movie = await fetch_movie(movie_id)
    cast = await fetch_movie_cast(movie_id)
    similar = await fetch_similar_movies(movie_id)

    ***REMOVED*** Return structured response
    return responses.detail(
        item=movie,
        related={"cast": cast, "similar_movies": similar},
        metadata={"aggregated_from": ["movies-db", "recommendation-service"]}
    )
```

***REMOVED******REMOVED******REMOVED*** Advanced Integration with Dependencies

```python
from fastapi import Depends
from typing import Optional

def get_response_builder() -> ResponseBuilder:
    """Dependency to provide configured ResponseBuilder."""
    return ResponseBuilder(config={
        "pagination": {"default_limit": 20},
        "detail": {"include_metadata": True}
    })

@router.get("/movies")
async def get_movies(
    page: int = 1,
    limit: int = 20,
    genre: Optional[str] = None,
    responses: ResponseBuilder = Depends(get_response_builder)
):
    ***REMOVED*** Fetch data with filters
    movies_data = await fetch_movies(page=page, limit=limit, genre=genre)

    return responses.paginated(
        items=movies_data["results"],
        page=page,
        limit=limit,
        total=movies_data["total"],
        metadata={
            "filters_applied": {"genre": genre} if genre else {},
            "query_time_ms": movies_data.get("query_time_ms")
        }
    )
```

***REMOVED******REMOVED*** Type Safety

All response types are fully typed with TypedDict:

```python
from fast_core.responses import (
    PaginatedResponse,
    DetailResponse,
    SearchResponse,
    ActionResponse,
    ErrorResponse,
    CollectionResponse
)

def process_paginated_response(response: PaginatedResponse) -> None:
    ***REMOVED*** Full type safety and IDE support
    results = response["results"]  ***REMOVED*** List[Any]
    pagination = response["pagination"]  ***REMOVED*** PaginationInfo
    page = pagination["page"]  ***REMOVED*** int
    total = pagination["total"]  ***REMOVED*** int
```

***REMOVED******REMOVED*** Best Practices

***REMOVED******REMOVED******REMOVED*** 1. Consistent Metadata

Include consistent metadata across all responses:

```python
def get_base_metadata() -> Dict[str, Any]:
    return {
        "api_version": "v1",
        "service": "movie-api",
        "timestamp": datetime.utcnow().isoformat()
    }

***REMOVED*** Use in responses
response = responses.paginated(
    items=movies,
    page=1,
    limit=20,
    total=100,
    metadata={
        **get_base_metadata(),
        "cache_hit": True,
        "query_time_ms": 45
    }
)
```

***REMOVED******REMOVED******REMOVED*** 2. Error Context

Provide helpful error context:

```python
def handle_movie_not_found(movie_id: int):
    return responses.error(
        code="MOVIE_NOT_FOUND",
        message=f"Movie with ID {movie_id} was not found",
        suggestions=[
            f"Check if movie ID {movie_id} is correct",
            "Browse popular movies at /movies?sort=popular",
            "Search for movies at /search?q=your_query"
        ],
        metadata={
            "requested_id": movie_id,
            "available_endpoints": ["/movies", "/search"]
        }
    )
```

***REMOVED******REMOVED******REMOVED*** 3. Performance Metadata

Include performance information:

```python
import time
from contextlib import contextmanager

@contextmanager
def timing():
    start = time.time()
    yield
    end = time.time()
    return (end - start) * 1000

async def get_movies_with_timing():
    with timing() as timer:
        movies_data = await fetch_movies()

    return responses.paginated(
        items=movies_data["results"],
        page=1,
        limit=20,
        total=movies_data["total"],
        metadata={
            "performance": {
                "query_time_ms": timer,
                "cache_hit": movies_data.get("from_cache", False)
            }
        }
    )
```

***REMOVED******REMOVED******REMOVED*** 4. Service Integration

Document service dependencies in metadata:

```python
async def get_movie_with_recommendations(movie_id: int):
    ***REMOVED*** Aggregate from multiple services
    movie = await movie_service.get_movie(movie_id)
    recommendations = await recommendation_service.get_similar(movie_id)
    user_data = await user_service.get_interactions(movie_id)

    return responses.detail(
        item=movie,
        related={"recommendations": recommendations},
        context={"user_interactions": user_data},
        metadata={
            "aggregated_from": [
                "movie-service",
                "recommendation-service",
                "user-service"
            ],
            "service_versions": {
                "movie-service": "v1.2.0",
                "recommendation-service": "v2.1.0",
                "user-service": "v1.0.0"
            }
        }
    )
```

***REMOVED******REMOVED*** Migration from Existing APIs

***REMOVED******REMOVED******REMOVED*** From Manual Dictionary Responses

**Before:**

```python
def get_movies():
    movies = fetch_movies()
    return {
        "results": movies,
        "total": len(movies),
        "page": 1,
        "per_page": 20
    }
```

**After:**

```python
def get_movies():
    movies_data = fetch_movies()
    return responses.paginated(
        items=movies_data["results"],
        page=1,
        limit=20,
        total=movies_data["total"]
    )
```

***REMOVED******REMOVED******REMOVED*** From Pydantic Models

You can continue using Pydantic models for validation while using ResponseBuilder for structure:

```python
from pydantic import BaseModel

class MovieResponse(BaseModel):
    id: int
    title: str
    year: int

def get_movie(movie_id: int) -> Dict[str, Any]:
    movie_data = fetch_movie(movie_id)
    movie = MovieResponse(**movie_data)  ***REMOVED*** Validate with Pydantic

    return responses.detail(
        item=movie.dict(),  ***REMOVED*** Convert to dict for ResponseBuilder
        metadata={"validated": True}
    )
```

***REMOVED******REMOVED*** Examples

See `examples/response_builder_example.py` for comprehensive usage examples demonstrating all response patterns with realistic data.
