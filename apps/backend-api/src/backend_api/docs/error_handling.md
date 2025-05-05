***REMOVED*** Standardized Error Handling

***REMOVED******REMOVED*** Overview

This application uses a consistent error handling approach across all services, queries, and API endpoints, providing:

1. **Clear Error Types**: Standard error classes with specific meanings
2. **Consistent Reporting**: Uniform error structures in API responses
3. **Centralized Translation**: Error types are automatically mapped to HTTP status codes
4. **Middleware Support**: Error handling middleware for global error processing

***REMOVED******REMOVED*** Standard Error Types

All application errors extend from the base `ServiceError` class:

| Error Class             | Description                            | HTTP Status               |
| ----------------------- | -------------------------------------- | ------------------------- |
| `ResourceNotFoundError` | Requested resource doesn't exist       | 404 Not Found             |
| `ValidationError`       | Invalid input data                     | 400 Bad Request           |
| `ConflictError`         | Operation conflicts with current state | 409 Conflict              |
| `PermissionError`       | User lacks required permissions        | 403 Forbidden             |
| `ServiceError`          | Base class for all other errors        | 500 Internal Server Error |

***REMOVED******REMOVED******REMOVED*** Example Usage

```python
***REMOVED*** In service or query class
def get_movie(self, movie_id: int) -> Movie:
    if movie_id <= 0:
        raise ValidationError(
            message="Invalid movie ID",
            field_errors={"movie_id": ["Must be positive"]}
        )

    movie = get_movie_by_id(movie_id)
    if not movie:
        raise ResourceNotFoundError(
            message=f"Movie with ID {movie_id} not found",
            resource_type="Movie",
            resource_id=movie_id
        )

    return movie
```

***REMOVED******REMOVED*** API Response Format

All API error responses follow this structure:

```json
{
  "message": "Clear error message",
  "details": {
    "field_errors": {
      "field_name": ["Error description"]
    },
    "additional_info": "More context if needed"
  }
}
```

***REMOVED******REMOVED*** Error Handling Middleware

The application includes a global error handling middleware that:

1. Catches all service errors
2. Logs appropriate error information
3. Converts errors to standard HTTP responses
4. Handles unexpected errors with a generic response

***REMOVED******REMOVED*** Implementation Details

***REMOVED******REMOVED******REMOVED*** In Routes

Routes should use the `service_error_to_http_exception` function:

```python
@router.get("/{movie_id}")
async def get_movie(movie_id: int):
    try:
        return movie_service.get_movie(movie_id)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)
```

***REMOVED******REMOVED******REMOVED*** Using Middleware

With the middleware approach, you can simplify route handlers:

```python
@router.get("/{movie_id}")
async def get_movie(movie_id: int):
    return movie_service.get_movie(movie_id)
    ***REMOVED*** Middleware will catch and process any ServiceErrors
```

***REMOVED******REMOVED*** Best Practices

1. **Be Specific**: Use the most specific error type for the situation
2. **Clear Messages**: Error messages should be clear and actionable
3. **Include Details**: Add relevant details to help troubleshoot the error
4. **Consistent Approach**: Follow the same pattern in all services and queries
5. **Document Errors**: API documentation should include possible error responses
