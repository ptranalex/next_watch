***REMOVED*** Errors Module

The errors module provides a comprehensive error handling system for FastAPI applications. It standardizes exception handling, error responses, and error formatting across Next Watch services.

***REMOVED******REMOVED*** Overview

This module contains three main components:

- **Exceptions**: Custom exception classes for different error types
- **Handlers**: Exception handlers that convert exceptions to HTTP responses
- **Responses**: Standardized error response models and utilities

***REMOVED******REMOVED*** Module Structure

***REMOVED******REMOVED******REMOVED*** `exceptions.py` - Custom Exception Classes

Defines a hierarchy of custom exceptions for different error scenarios.

***REMOVED******REMOVED******REMOVED******REMOVED*** Base Exception

- `APIException`: Base class for all API exceptions

***REMOVED******REMOVED******REMOVED******REMOVED*** Specific Exception Types

- `ValidationException`: Input validation errors (400 Bad Request)
- `AuthenticationException`: Authentication failures (401 Unauthorized)
- `AuthorizationException`: Authorization failures (403 Forbidden)
- `ResourceNotFoundException`: Resource not found (404 Not Found)
- `ConflictException`: Resource conflicts (409 Conflict)
- `BusinessLogicException`: Business rule violations (422 Unprocessable Entity)
- `RateLimitException`: Rate limit exceeded (429 Too Many Requests)
- `ExternalServiceException`: External service failures (502 Bad Gateway)
- `ServiceUnavailableException`: Service unavailable (503 Service Unavailable)

***REMOVED******REMOVED******REMOVED******REMOVED*** Usage Examples

```python
from fast_core.errors.exceptions import (
    ValidationException,
    ResourceNotFoundException,
    AuthorizationException
)

***REMOVED*** Validation error
if not user_data.email:
    raise ValidationException(
        message="Email is required",
        field="email"
    )

***REMOVED*** Resource not found
user = await get_user(user_id)
if not user:
    raise ResourceNotFoundException(
        message=f"User with ID {user_id} not found",
        resource_type="User",
        resource_id=user_id
    )

***REMOVED*** Authorization error
if not user.has_permission("admin"):
    raise AuthorizationException(
        message="Admin permission required",
        required_permissions=["admin"]
    )
```

***REMOVED******REMOVED******REMOVED*** `handlers.py` - Exception Handlers

Converts exceptions into standardized HTTP responses.

***REMOVED******REMOVED******REMOVED******REMOVED*** Setup

```python
from fastapi import FastAPI
from fast_core.errors import setup_exception_handlers

app = FastAPI()
setup_exception_handlers(app)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Custom Handler Registration

```python
from fast_core.errors.handlers import get_exception_handlers

***REMOVED*** Get all handlers
handlers = get_exception_handlers()

***REMOVED*** Register with FastAPI
for exception_class, handler in handlers.items():
    app.add_exception_handler(exception_class, handler)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Handler Behavior

Each handler:

- Logs the exception with appropriate level
- Creates standardized error response
- Includes request ID for tracing
- Masks sensitive information
- Returns appropriate HTTP status code

***REMOVED******REMOVED******REMOVED*** `responses.py` - Error Response Models

Provides standardized response models and utilities for consistent error formatting.

***REMOVED******REMOVED******REMOVED******REMOVED*** Response Models

```python
from fast_core.errors.responses import (
    ErrorDetail,
    ValidationErrorDetail,
    AuthorizationErrorDetail,
    SuccessResponse,
    PaginatedResponse
)

***REMOVED*** Basic error detail
error = ErrorDetail(
    message="Something went wrong",
    code="INTERNAL_ERROR",
    request_id="req-123"
)

***REMOVED*** Validation error with field details
validation_error = ValidationErrorDetail(
    message="Validation failed",
    field="email",
    value="invalid-email",
    constraint="email_format"
)

***REMOVED*** Success response
success = SuccessResponse(
    data={"user_id": 123},
    message="User created successfully"
)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Response Utilities

```python
from fast_core.errors.responses import (
    create_error_response,
    create_success_response,
    create_validation_error_response,
    create_paginated_response
)

***REMOVED*** Create error response
error_response = create_error_response(
    message="User not found",
    status_code=404,
    error_code="USER_NOT_FOUND"
)

***REMOVED*** Create success response
success_response = create_success_response(
    data=user_data,
    message="User retrieved successfully"
)

***REMOVED*** Create validation error response
validation_response = create_validation_error_response([
    {"field": "email", "message": "Invalid email format"},
    {"field": "age", "message": "Must be at least 18"}
])
```

***REMOVED******REMOVED*** Integration with FastAPI

***REMOVED******REMOVED******REMOVED*** Complete Setup

```python
from fastapi import FastAPI
from fast_core.errors import setup_exception_handlers
from fast_core.errors.responses import STANDARD_RESPONSES

app = FastAPI(
    responses=STANDARD_RESPONSES  ***REMOVED*** Add standard error responses to OpenAPI
)

***REMOVED*** Setup exception handlers
setup_exception_handlers(app)

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await fetch_user(user_id)
    if not user:
        raise ResourceNotFoundException(
            message=f"User {user_id} not found",
            resource_type="User",
            resource_id=user_id
        )
    return create_success_response(data=user)
```

***REMOVED******REMOVED******REMOVED*** Route-Level Error Handling

```python
from fastapi import HTTPException
from fast_core.errors.exceptions import ValidationException

@app.post("/users")
async def create_user(user_data: UserCreate):
    try:
        ***REMOVED*** Validate business rules
        if await email_exists(user_data.email):
            raise ConflictException(
                message="Email already exists",
                resource_type="User",
                conflict_field="email"
            )

        ***REMOVED*** Create user
        user = await create_user_in_db(user_data)
        return create_success_response(
            data=user,
            message="User created successfully"
        )

    except ValidationException as e:
        ***REMOVED*** Will be handled by validation exception handler
        raise
    except Exception as e:
        ***REMOVED*** Log unexpected errors
        logger.exception("Unexpected error creating user")
        raise APIException(
            message="Failed to create user",
            status_code=500
        )
```

***REMOVED******REMOVED*** Error Response Format

All error responses follow a consistent format:

***REMOVED******REMOVED******REMOVED*** Single Error Response

```json
{
  "error": {
    "message": "User not found",
    "code": "USER_NOT_FOUND",
    "request_id": "req-abc123",
    "timestamp": "2024-01-15T10:30:00Z",
    "details": {
      "resource_type": "User",
      "resource_id": "123"
    }
  }
}
```

***REMOVED******REMOVED******REMOVED*** Validation Error Response

```json
{
  "error": {
    "message": "Validation failed",
    "code": "VALIDATION_ERROR",
    "request_id": "req-abc123",
    "timestamp": "2024-01-15T10:30:00Z",
    "validation_errors": [
      {
        "field": "email",
        "message": "Invalid email format",
        "value": "invalid-email",
        "constraint": "email_format"
      }
    ]
  }
}
```

***REMOVED******REMOVED******REMOVED*** Success Response

```json
{
  "data": {
    "user_id": 123,
    "username": "john_doe"
  },
  "message": "User retrieved successfully",
  "request_id": "req-abc123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

***REMOVED******REMOVED*** Configuration

Error handling can be configured through environment variables:

```bash
***REMOVED*** Error Handling
ERROR_INCLUDE_STACK_TRACE=false
ERROR_MASK_SENSITIVE_DATA=true
ERROR_LOG_LEVEL=ERROR
ERROR_INCLUDE_REQUEST_DETAILS=true
```

***REMOVED******REMOVED*** Best Practices

***REMOVED******REMOVED******REMOVED*** Exception Usage

1. **Use specific exceptions**: Choose the most appropriate exception type
2. **Provide clear messages**: Include actionable information for users
3. **Include context**: Add relevant details like resource IDs
4. **Don't expose internals**: Avoid revealing system implementation details

***REMOVED******REMOVED******REMOVED*** Error Handling

1. **Handle at appropriate level**: Catch exceptions where you can handle them
2. **Log with context**: Include request ID and relevant details
3. **Fail fast**: Validate inputs early and throw exceptions immediately
4. **Provide fallbacks**: Handle external service failures gracefully

***REMOVED******REMOVED******REMOVED*** Response Design

1. **Consistent format**: Always use standardized response models
2. **Include request ID**: Essential for debugging and tracing
3. **Appropriate status codes**: Use correct HTTP status codes
4. **Clear error messages**: Make messages user-friendly but informative

***REMOVED******REMOVED*** Testing

***REMOVED******REMOVED******REMOVED*** Exception Testing

```python
import pytest
from fast_core.errors.exceptions import ValidationException, ResourceNotFoundException

def test_validation_exception():
    with pytest.raises(ValidationException) as exc_info:
        raise ValidationException(
            message="Email is required",
            field="email"
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.field == "email"

def test_resource_not_found():
    with pytest.raises(ResourceNotFoundException) as exc_info:
        raise ResourceNotFoundException(
            message="User not found",
            resource_type="User",
            resource_id=123
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.resource_type == "User"
```

***REMOVED******REMOVED******REMOVED*** Handler Testing

```python
from fastapi.testclient import TestClient
from fast_core.errors import setup_exception_handlers

def test_exception_handler(client: TestClient):
    response = client.get("/users/999")  ***REMOVED*** Non-existent user

    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "USER_NOT_FOUND"
    assert "request_id" in data["error"]
```

***REMOVED******REMOVED*** Integration with Next Watch Services

The errors module integrates with:

- **CLI Library**: Consistent error logging and formatting
- **Config Library**: Environment-based error handling configuration
- **Cache Library**: Graceful handling of cache failures
- **All APIs**: Standardized error responses across services

***REMOVED******REMOVED*** OpenAPI Documentation

Error responses are automatically included in OpenAPI documentation:

```python
from fast_core.errors.responses import STANDARD_RESPONSES

app = FastAPI(responses=STANDARD_RESPONSES)

@app.get("/users/{user_id}", responses={
    404: {"model": ErrorDetail},
    422: {"model": ValidationErrorDetail}
})
async def get_user(user_id: int):
    ***REMOVED*** Implementation
    pass
```

This ensures that API documentation includes comprehensive error response examples for all endpoints.
