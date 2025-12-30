# Routes Module

The routes module contains all FastAPI route handlers for the Auth API service. It provides the HTTP interface for authentication operations, health monitoring, and service management. Each route module is organized by domain and follows consistent patterns for request handling, validation, and response formatting.

## Overview

The routes module provides:

- **Authentication Endpoints**: User registration, login, token management
- **Health Monitoring**: Service and database health checks
- **Service Information**: Metadata and status endpoints
- **Token Verification**: JWT token validation for other services
- **Admin Operations**: Administrative endpoints for user management

## Architecture

### Route Organization

- **`auth.py`** (9.8KB, 328 lines): Core authentication endpoints
- **`health.py`** (10KB, 307 lines): Health monitoring and status endpoints
- **`meta.py`** (743B, 31 lines): Basic service information endpoints

### Design Patterns

- **Domain-Based Grouping**: Routes organized by functional domain
- **Consistent Response Format**: Standardized JSON response structures
- **Error Handling**: Comprehensive error handling with appropriate HTTP status codes
- **Dependency Injection**: FastAPI dependency injection for authentication and validation
- **Type Safety**: Full type hints and Pydantic model validation

## Route Modules

### `auth.py` - Authentication Routes

Core authentication functionality for user management and token operations.

#### Endpoints

```http
POST /auth/register     # Register new user account
POST /auth/login        # Login with form data (compatibility)
POST /auth/login/json   # Login with JSON payload
POST /auth/refresh      # Refresh access token using refresh token
GET  /auth/me          # Get current authenticated user information
POST /auth/verify-token # Verify JWT token (for BFF service)
```

#### Key Features

- **Multiple Login Formats**: Supports both form data and JSON login
- **Token Management**: Access and refresh token handling
- **User Registration**: Secure user account creation with validation
- **Token Verification**: Dedicated endpoint for service-to-service verification
- **Rate Limiting**: Built-in protection against abuse
- **Input Validation**: Comprehensive request validation using Pydantic

#### Request/Response Examples

**User Registration:**

```python
# Request
POST /auth/register
{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
}

# Response (201 Created)
{
    "id": 1,
    "email": "user@example.com",
    "username": "testuser",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "last_login": null
}
```

**User Login:**

```python
# Request
POST /auth/login/json
{
    "email": "user@example.com",
    "password": "securepassword123"
}

# Response (200 OK)
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "testuser"
    }
}
```

**Token Verification (BFF Usage):**

```python
# Request
POST /auth/verify-token
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

# Response (200 OK)
{
    "valid": true,
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "testuser",
        "is_active": true
    },
    "expires_at": "2024-01-01T01:00:00Z"
}

# Response (401 Unauthorized)
{
    "valid": false,
    "error": "Token has expired",
    "code": "TOKEN_EXPIRED"
}
```

#### Error Handling

```python
# Authentication errors
{
    "detail": "Invalid credentials",
    "code": "INVALID_CREDENTIALS",
    "type": "authentication_error"
}

# Validation errors
{
    "detail": "Validation failed",
    "errors": [
        {
            "field": "email",
            "message": "Invalid email format"
        }
    ],
    "type": "validation_error"
}
```

### `health.py` - Health Monitoring Routes

Comprehensive health monitoring endpoints for service orchestration and monitoring.

#### Endpoints

```http
GET /health         # Comprehensive health check with database status
GET /health/live    # Liveness probe for load balancers
GET /health/ready   # Readiness probe for Kubernetes/orchestrators
GET /db-health      # Legacy database health check (backward compatibility)
```

#### Key Features

- **Multiple Health Types**: Different endpoints for different monitoring needs
- **Database Monitoring**: PostgreSQL health and performance tracking
- **Response Time Tracking**: Performance metrics included in responses
- **Graceful Degradation**: Handles database unavailability gracefully
- **Orchestration Ready**: Kubernetes-compatible liveness/readiness probes

#### Response Examples

**Comprehensive Health Check:**

```python
# Response (200 OK)
GET /health
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00Z",
    "response_time_ms": 45.2,
    "version": "1.0.0",
    "environment": "production",
    "database": {
        "healthy": true,
        "response_time_ms": 12.3,
        "version": "PostgreSQL 15.4",
        "size_mb": 256.7,
        "connections": {
            "active": 5,
            "max": 100
        }
    }
}

# Response (503 Service Unavailable)
{
    "status": "unhealthy",
    "timestamp": "2024-01-01T12:00:00Z",
    "response_time_ms": 5021.1,
    "version": "1.0.0",
    "environment": "production",
    "database": {
        "healthy": false,
        "error": "Connection timeout",
        "response_time_ms": 5000.0
    }
}
```

**Liveness Probe:**

```python
# Response (200 OK)
GET /health/live
{
    "status": "alive",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

**Readiness Probe:**

```python
# Response (200 OK)
GET /health/ready
{
    "status": "ready",
    "timestamp": "2024-01-01T12:00:00Z",
    "checks": {
        "database": "healthy",
        "auth_service": "ready"
    }
}

# Response (503 Service Unavailable)
{
    "status": "not_ready",
    "timestamp": "2024-01-01T12:00:00Z",
    "checks": {
        "database": "unhealthy",
        "auth_service": "ready"
    }
}
```

### `meta.py` - Service Information Routes

Basic service information and metadata endpoints.

#### Endpoints

```http
GET /              # Service information and welcome message
```

#### Response Example

```python
# Response (200 OK)
GET /
{
    "message": "Auth API Service",
    "version": "1.0.0",
    "environment": "production",
    "documentation": "/docs",
    "health": "/health"
}
```

## Route Implementation Patterns

### Standard Route Structure

```python
from fastapi import APIRouter, Depends, HTTPException, status
from auth_api.schemas import RequestSchema, ResponseSchema
from auth_api.services import auth_service
from auth_api.dependencies import get_current_user

router = APIRouter(prefix="/endpoint", tags=["endpoint"])

@router.post("/action", response_model=ResponseSchema)
async def endpoint_action(
    request: RequestSchema,
    current_user: User = Depends(get_current_user)
) -> ResponseSchema:
    """
    Endpoint action description.

    Args:
        request: Validated request data
        current_user: Authenticated user (if required)

    Returns:
        ResponseSchema: Formatted response data

    Raises:
        HTTPException: Various HTTP errors based on business logic
    """
    try:
        result = await auth_service.perform_action(request)
        return ResponseSchema.from_result(result)
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

### Error Handling Patterns

```python
# Authentication required
@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
    # Will automatically return 401 if not authenticated
    pass

# Custom business logic errors
try:
    result = await auth_service.some_operation()
except ValidationError as e:
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={"error": "validation_failed", "details": str(e)}
    )
except PermissionError as e:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"error": "permission_denied", "message": str(e)}
    )
except NotFoundError as e:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": "not_found", "message": str(e)}
    )
```

### Response Model Patterns

```python
# Success response with data
class SuccessResponse(BaseModel):
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

# Error response
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

# Paginated response
class PaginatedResponse(BaseModel):
    data: List[Any]
    pagination: Dict[str, Any] = Field(
        description="Pagination metadata"
    )
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
```

## Security Implementation

### Authentication Dependencies

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Extract and validate user from JWT token."""
    token = credentials.credentials
    user = await auth_service.verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return user

async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure current user has admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(request: Request, login_data: LoginRequest):
    # Login logic here
    pass
```

### Input Validation

```python
from pydantic import BaseModel, validator, EmailStr

class UserRegistrationRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    password_confirm: str

    @validator('password')
    def validate_password_strength(cls, v):
        """Ensure password meets security requirements."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain number')
        return v

    @validator('password_confirm')
    def passwords_match(cls, v, values):
        """Ensure password confirmation matches."""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
```

## Testing Routes

### Test Structure

```python
import pytest
from fastapi.testclient import TestClient
from auth_api.main import app

client = TestClient(app)

class TestAuthRoutes:
    def test_register_user_success(self):
        """Test successful user registration."""
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123",
            "password_confirm": "SecurePass123"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "password" not in data  # Ensure password not in response

    def test_register_user_invalid_email(self):
        """Test registration with invalid email."""
        response = client.post("/auth/register", json={
            "email": "invalid-email",
            "username": "testuser",
            "password": "SecurePass123",
            "password_confirm": "SecurePass123"
        })
        assert response.status_code == 422

    def test_login_success(self):
        """Test successful user login."""
        # First register a user
        client.post("/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123",
            "password_confirm": "SecurePass123"
        })

        # Then test login
        response = client.post("/auth/login/json", json={
            "email": "test@example.com",
            "password": "SecurePass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token."""
        response = client.get("/auth/me")
        assert response.status_code == 401
```

### Health Route Tests

```python
class TestHealthRoutes:
    def test_health_check(self):
        """Test comprehensive health check."""
        response = client.get("/health")
        assert response.status_code in [200, 503]  # Healthy or unhealthy
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "database" in data

    def test_liveness_probe(self):
        """Test liveness probe."""
        response = client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"

    def test_readiness_probe(self):
        """Test readiness probe."""
        response = client.get("/health/ready")
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert "checks" in data
```

## Best Practices

### Route Design

1. **RESTful Patterns**: Follow REST conventions for HTTP methods and URLs
2. **Consistent Responses**: Use consistent response formats across endpoints
3. **Proper Status Codes**: Return appropriate HTTP status codes
4. **Documentation**: Include comprehensive docstrings and OpenAPI documentation
5. **Validation**: Validate all inputs using Pydantic models

### Performance

1. **Async Operations**: Use async/await for all database and external service calls
2. **Database Connections**: Use connection pooling efficiently
3. **Caching**: Implement caching for frequently accessed data
4. **Pagination**: Implement pagination for endpoints returning lists
5. **Rate Limiting**: Protect against abuse with appropriate rate limits

### Security

1. **Authentication**: Require authentication for protected endpoints
2. **Authorization**: Implement role-based access control where needed
3. **Input Sanitization**: Validate and sanitize all inputs
4. **Error Messages**: Don't expose sensitive information in error messages
5. **HTTPS Only**: Ensure all endpoints use HTTPS in production

### Monitoring

1. **Logging**: Log important events and errors appropriately
2. **Metrics**: Include performance metrics in responses
3. **Health Checks**: Implement comprehensive health monitoring
4. **Error Tracking**: Monitor and alert on error rates
5. **Performance Monitoring**: Track response times and database performance

## Contributing

When adding new routes:

1. **Follow Patterns**: Use existing routes as templates
2. **Add Tests**: Include comprehensive test coverage
3. **Document APIs**: Update OpenAPI documentation
4. **Security Review**: Ensure proper authentication and authorization
5. **Performance Testing**: Test under load conditions

## Dependencies

Routes depend on:

- **FastAPI**: Web framework and dependency injection
- **Pydantic**: Request/response validation
- **Authentication Services**: User authentication and token management
- **Health Services**: System monitoring and health checks
- **Database**: Data persistence and retrieval
