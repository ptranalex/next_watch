***REMOVED*** Routes Module

This module defines all the API routes and endpoints for the Recommendation API service, organizing them into versioned API groups.

***REMOVED******REMOVED*** Overview

The routes module provides:

- FastAPI route definitions
- Request handling and response formatting
- Input validation and error handling
- API versioning
- OpenAPI documentation integration

***REMOVED******REMOVED*** Structure

```
routes/
├── __init__.py      ***REMOVED*** Package initialization and exports
├── api_v1.py        ***REMOVED*** Main router for API version 1
└── v1/              ***REMOVED*** Version 1 route modules
    ├── __init__.py  ***REMOVED*** Package initialization
    ├── movies.py    ***REMOVED*** Movie-related endpoints
    ├── users.py     ***REMOVED*** User-related endpoints
    └── recommendations.py  ***REMOVED*** Recommendation endpoints
```

***REMOVED******REMOVED*** API Version 1 Endpoints

***REMOVED******REMOVED******REMOVED*** Movies Endpoints

```
GET /api/v1/movies                  ***REMOVED*** List movies with optional filtering
GET /api/v1/movies/{movie_id}       ***REMOVED*** Get a specific movie by ID
GET /api/v1/movies/popular          ***REMOVED*** Get popular movies
GET /api/v1/movies/trending         ***REMOVED*** Get trending movies
GET /api/v1/movies/search           ***REMOVED*** Search movies by title or other criteria
```

***REMOVED******REMOVED******REMOVED*** Users Endpoints

```
GET /api/v1/users/{user_id}         ***REMOVED*** Get user profile
POST /api/v1/users                  ***REMOVED*** Create a new user
PUT /api/v1/users/{user_id}         ***REMOVED*** Update user profile
GET /api/v1/users/{user_id}/ratings ***REMOVED*** Get user ratings
POST /api/v1/users/{user_id}/ratings ***REMOVED*** Add a new rating
```

***REMOVED******REMOVED******REMOVED*** Recommendations Endpoints

```
GET /api/v1/recommendations                    ***REMOVED*** Get general recommendations
GET /api/v1/recommendations/user/{user_id}     ***REMOVED*** Get user-specific recommendations
GET /api/v1/recommendations/similar/{movie_id} ***REMOVED*** Get similar movies
GET /api/v1/recommendations/trending           ***REMOVED*** Get trending recommendations
GET /api/v1/recommendations/popular            ***REMOVED*** Get popular recommendations
```

***REMOVED******REMOVED*** Usage

***REMOVED******REMOVED******REMOVED*** Including Routes in the Application

The routes are included in the main FastAPI application like this:

```python
from fastapi import FastAPI
from recommendation_api.routes.api_v1 import api_v1_router

app = FastAPI()
app.include_router(api_v1_router, prefix="/api/v1")
```

***REMOVED******REMOVED******REMOVED*** Creating a New Endpoint

To add a new endpoint to the API:

1. Add the route function to the appropriate module in `v1/`
2. Use FastAPI decorators for HTTP method and path
3. Add Pydantic models for request/response
4. Add route function to the router

Example:

```python
***REMOVED*** In routes/v1/movies.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from recommendation_api.models.movie import Movie
from recommendation_api.db.operations import get_movie_by_id

router = APIRouter()

@router.get("/{movie_id}", response_model=Movie)
async def get_movie(movie_id: int):
    movie = get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie
```

***REMOVED******REMOVED*** Error Handling

The routes implement consistent error handling:

- HTTP exceptions with appropriate status codes
- Error response bodies with detail messages
- Input validation using Pydantic models
- Exception handlers for common errors

***REMOVED******REMOVED*** Authentication

Some routes require authentication:

- User-specific recommendations require user authentication
- Profile updates require user authentication
- Rating submissions require user authentication

Authentication is implemented using:

- JWT tokens
- API keys for service-to-service communication
- Rate limiting for unauthenticated requests

***REMOVED******REMOVED*** Documentation

API documentation is available at:

- `/docs` - Swagger UI
- `/redoc` - ReDoc documentation

Documentation is generated automatically from:

- Route path definitions
- Pydantic models
- Docstrings
- Example values
