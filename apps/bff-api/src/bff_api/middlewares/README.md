***REMOVED*** BFF API Middlewares

This module provides FastAPI middleware components that process HTTP requests and responses, applying cross-cutting concerns across the entire API.

***REMOVED******REMOVED*** Structure

The middlewares module is organized as follows:

```
bff_api/middlewares/
│
├── __init__.py   ***REMOVED*** Package initialization and middleware registration
├── logging.py    ***REMOVED*** Request/response logging middleware
└── auth.py       ***REMOVED*** Authentication and authorization middleware
```

***REMOVED******REMOVED*** Middleware Components

***REMOVED******REMOVED******REMOVED*** Authentication Middleware

The `AuthMiddleware` in `auth.py` handles:

- JWT token validation and verification
- User authentication state management
- Role-based access control
- API key validation for service-to-service communication
- Security headers enforcement

***REMOVED******REMOVED******REMOVED*** Logging Middleware

The `LoggingMiddleware` in `logging.py` provides:

- Request/response logging with configurable verbosity
- Performance timing for requests
- Correlation ID tracking across services
- Error tracking and aggregation
- PII (Personally Identifiable Information) filtering in logs

***REMOVED******REMOVED*** Usage

Middlewares are registered in the FastAPI application startup sequence in `main.py`:

```python
def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="BFF API",
        description="Backend for Frontend API for Next Watch",
        version="0.1.0",
    )

    ***REMOVED*** Register middlewares
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        AuthMiddleware,
        exclude_paths=["/api/v1/health", "/docs", "/redoc"]
    )

    ***REMOVED*** ... other app configuration ...

    return app
```

***REMOVED******REMOVED*** Middleware Order

The order of middleware registration is important as they are executed in reverse order (last registered is executed first):

1. Authentication middleware (executes first)
2. Logging middleware (executes second)

This ensures that authentication information is available to the logging middleware.

***REMOVED******REMOVED*** Design Principles

1. **Minimal Impact**: Middlewares should have minimal performance impact
2. **Separation of Concerns**: Each middleware handles a specific cross-cutting concern
3. **Configuration**: Middlewares should be configurable at startup
4. **Fail-Safe**: Middlewares should not break the application flow
5. **Transparent**: Their behavior should be predictable and well-documented

***REMOVED******REMOVED*** Implementation Details

***REMOVED******REMOVED******REMOVED*** Error Handling

Middlewares implement careful error handling to:

- Prevent middleware errors from breaking the request flow
- Log middleware errors appropriately
- Return appropriate error responses when needed

***REMOVED******REMOVED******REMOVED*** Configuration

Middlewares can be configured via:

- Environment variables
- Constructor parameters
- Global settings

***REMOVED******REMOVED******REMOVED*** Performance Considerations

To minimize performance impact:

- Middlewares use async/await for I/O operations
- Heavy processing is avoided in the request path
- Caching is used where appropriate
- Early returns are implemented for excluded paths

***REMOVED******REMOVED*** Extension Guidelines

When adding new middlewares:

1. Create a new file in the middlewares directory
2. Implement the middleware following FastAPI's middleware pattern
3. Register the middleware in the application startup
4. Document the middleware's purpose and configuration
5. Add appropriate tests

***REMOVED******REMOVED*** Best Practices

- Keep middlewares focused on a single responsibility
- Use exclude_paths for endpoints that don't need processing
- Log middleware actions at appropriate levels
- Consider the performance impact of each middleware
- Order middlewares carefully based on dependencies between them
