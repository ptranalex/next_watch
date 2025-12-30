# Routes Module

This module defines all the API routes and endpoints for the Recommendation API service, organizing them into logical groups with proper separation of concerns.

## Overview

The routes module provides:

- FastAPI route definitions with APIRouter
- Request handling and response formatting
- Input validation and error handling
- Health check endpoints
- Meta information endpoints
- API versioning
- OpenAPI documentation integration

## Structure

```
routes/
├── __init__.py         # Package initialization and exports
├── api_v1.py          # Main router for API version 1
├── meta.py            # Meta endpoints (root, API info)
├── health.py          # Health check endpoints
└── v1/                # Version 1 route modules
    ├── __init__.py    # Package initialization
    ├── personalized.py # Personalized recommendation endpoints
    ├── popular.py     # Popular movie endpoints
    ├── similar.py     # Similar movie endpoints
    └── trending.py    # Trending movie endpoints
```

## Core Endpoints

### Meta Endpoints (`meta.py`)

```
GET /                   # Root endpoint with API information
```

Returns API information including:

- Welcome message
- Available API versions
- Health check endpoints
- Documentation links

### Health Check Endpoints (`health.py`)

```
GET /health            # Comprehensive health check
GET /health/live       # Simple liveness check
GET /health/ready      # Readiness check for critical dependencies
```

Health checks monitor:

- PostgreSQL database connectivity
- Redis cache connectivity
- Qdrant vector database connectivity

## API Version 1 Endpoints

### Recommendation Endpoints

```
GET /reco/v1/recommendations/personalized/{user_id}  # Personalized recommendations
GET /reco/v1/recommendations/popular                 # Popular movies
GET /reco/v1/recommendations/similar/{movie_id}      # Similar movies
GET /reco/v1/recommendations/trending                # Trending movies
```

## Usage

### Including Routes in the Application

The routes are included in the main FastAPI application using the modular structure:

```python
from fastapi import FastAPI
from recommendation_api.routes.meta import router as meta_router
from recommendation_api.routes.health import router as health_router
from recommendation_api.routes import api_v1_router

app = FastAPI()

# Include routers with appropriate tags
app.include_router(meta_router, tags=["meta"])
app.include_router(health_router, tags=["health"])
app.include_router(api_v1_router, prefix="/reco", tags=["reco-v1"])
```

### Creating a New Route Module

To add a new route module:

1. Create a new file in the appropriate directory
2. Define an APIRouter instance
3. Add route functions with FastAPI decorators
4. Export the router in the module's `__init__.py`

Example:

```python
# In routes/v1/new_feature.py
from fastapi import APIRouter, HTTPException
from typing import List
from recommendation_api.models.response import FeatureResponse

router = APIRouter()

@router.get("/feature", response_model=List[FeatureResponse])
async def get_feature():
    """Get feature data."""
    try:
        # Implementation here
        return feature_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Adding Routes to Existing Modules

To add a new endpoint to an existing module:

1. Add the route function to the appropriate module
2. Use FastAPI decorators for HTTP method and path
3. Add Pydantic models for request/response validation
4. Include proper error handling

## Health Check Implementation

The health check system provides comprehensive monitoring:

### Comprehensive Health Check (`/health`)

- Checks all dependencies (PostgreSQL, Redis, Qdrant)
- Returns detailed status for each service
- Includes response times and connection details
- Returns HTTP 200 if all healthy, 503 if any unhealthy

### Liveness Check (`/health/live`)

- Simple endpoint that returns if the service is running
- No dependency checks
- Used by load balancers and orchestrators
- Always returns HTTP 200 if service is responsive

### Readiness Check (`/health/ready`)

- Checks critical dependencies only (PostgreSQL, Qdrant)
- Redis is considered non-critical
- Returns HTTP 200 if ready, 503 if not ready
- Used to determine if service can handle requests

## Error Handling

The routes implement consistent error handling:

- HTTP exceptions with appropriate status codes
- Structured error response bodies with detail messages
- Input validation using Pydantic models
- Global exception handlers for unhandled errors
- Proper logging of errors with context

Example error response:

```json
{
  "detail": "Movie not found",
  "status_code": 404,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Response Models

All endpoints use Pydantic models for response validation:

- Consistent response structure
- Automatic OpenAPI schema generation
- Type safety and validation
- Clear documentation

## Authentication & Authorization

Currently, the API operates without authentication, but the structure supports:

- JWT token authentication
- API key authentication for service-to-service communication
- Rate limiting for unauthenticated requests
- User context for personalized recommendations

## Documentation

API documentation is automatically generated and available at:

- `/docs` - Swagger UI with interactive testing
- `/redoc` - ReDoc documentation with better formatting

Documentation includes:

- All route definitions with parameters
- Request/response schemas
- Example values and responses
- Error codes and descriptions
- Health check endpoint details

## Testing

Routes can be tested using:

```bash
# Test health endpoints
curl http://localhost:8002/health
curl http://localhost:8002/health/live
curl http://localhost:8002/health/ready

# Test meta endpoints
curl http://localhost:8002/

# Test recommendation endpoints
curl http://localhost:8002/reco/v1/recommendations/popular
```

## Best Practices

When working with routes:

1. **Use APIRouter**: Always use APIRouter for modular route organization
2. **Proper Tags**: Tag routes appropriately for OpenAPI documentation
3. **Error Handling**: Include proper exception handling in all routes
4. **Response Models**: Use Pydantic models for all responses
5. **Documentation**: Add docstrings to all route functions
6. **Validation**: Validate all inputs using Pydantic models
7. **Logging**: Log important events and errors with context
