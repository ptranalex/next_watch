# BFF API Service Clients

This module provides client implementations for communicating with backend services. These clients handle the HTTP communication, error handling, retries, and response processing for all backend service interactions.

## Structure

The services module is organized as follows:

```
bff_api/services/
│
├── __init__.py       # Package initialization
├── backend_client.py # Client for the Backend API service
└── auth_client.py    # Client for the Auth API service
```

## Service Clients

### BackendClient

The `BackendClient` provides methods for accessing the main Backend API, including:

- **Movies**: Search, details, recommendations, ratings, reviews, watchlist
- **TV Shows**: Search, details, seasons, episodes, ratings, reviews, watchlist
- **People**: Search, details, credits, filmography
- **Users**: Profiles, preferences, activity, watch history
- **Search**: Global search across content types
- **Categories**: Genres, keywords, collections

### AuthClient

The `AuthClient` provides authentication and authorization methods:

- **Authentication**: Login, register, token refresh, validation
- **Authorization**: Permission checks, role management
- **Profile**: User profile management
- **Security**: Password reset, account verification

## Usage

The service clients are designed to be used as dependencies in the FastAPI routes:

```python
from fastapi import Depends
from bff_api.dependencies.common import get_backend_client, get_auth_client
from bff_api.services.backend_client import BackendClient
from bff_api.services.auth_client import AuthClient

@router.get("/movies/{movie_id}")
async def get_movie(
    movie_id: int,
    backend_client: BackendClient = Depends(get_backend_client)
):
    """Get movie details."""
    return await backend_client.get_movie(movie_id)

@router.post("/auth/login")
async def login(
    credentials: LoginRequest,
    auth_client: AuthClient = Depends(get_auth_client)
):
    """User login."""
    return await auth_client.login(credentials.username, credentials.password)
```

## Design Principles

1. **Separation of Concerns**: The service clients abstract away the details of HTTP communication from the route handlers
2. **Resilience**: Built-in retry mechanisms with exponential backoff for handling transient failures
3. **Error Handling**: Consistent error handling and mapping of backend errors to appropriate HTTP responses
4. **Performance**: Asynchronous communication for optimal performance
5. **Caching**: Support for response caching to reduce backend load
6. **Typed Interfaces**: Full type annotations for all methods and responses
7. **Logging**: Comprehensive logging for debugging and monitoring

## Implementation Details

### HTTP Client

The clients use `httpx` for HTTP communication, which provides:

- Async support
- Timeout handling
- Connection pooling
- HTTP/2 support
- Request/response logging

### Retry Logic

The `tenacity` library is used for implementing retry logic with:

- Configurable retry attempts
- Exponential backoff
- Jitter to prevent thundering herd
- Retry only on specific error conditions

### Error Handling

Errors from the backend services are:

1. Categorized by type (authentication, validation, resource, server)
2. Mapped to appropriate HTTP status codes
3. Enhanced with additional context when needed
4. Properly logged with relevant details

## Extension Guidelines

When extending or modifying the service clients:

1. Maintain consistent method signatures
2. Ensure all methods are properly typed
3. Follow the existing error handling patterns
4. Add comprehensive docstrings
5. Update unit tests for new functionality
6. Consider caching implications for read operations
7. Ensure proper retry configuration for different operation types

## Best Practices

- Use appropriate timeouts for different types of operations
- Include relevant request IDs in logs for traceability
- Handle authentication token refreshes automatically
- Implement circuit breakers for failing services
- Cache idempotent responses when appropriate
- Use bulk operations where available to reduce network overhead
- Log performance metrics for identifying bottlenecks
