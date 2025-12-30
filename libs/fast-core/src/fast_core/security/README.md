# Security Module

The security module provides essential security utilities for FastAPI applications, including JWT token management and rate limiting. These components help secure Next Watch services with industry-standard practices.

## Overview

This module contains two main security components:

- **JWT Management**: Token creation, validation, and refresh handling
- **Rate Limiting**: Request throttling with multiple backend options

## Module Structure

### `jwt.py` - JWT Token Management

Provides comprehensive JWT token handling with access and refresh token support.

#### Key Classes

- `JWTConfig`: Configuration for JWT settings
- `JWTManager`: Main JWT operations manager
- `TokenData`: Token payload data structure

#### Basic Usage

```python
from fast_core.security.jwt import create_jwt_manager, JWTConfig

# Configure JWT
config = JWTConfig(
    secret_key="your-secret-key",
    algorithm="HS256",
    access_token_expire_minutes=30,
    refresh_token_expire_days=7
)

# Create manager
jwt_manager = create_jwt_manager(config)

# Create tokens
access_token = jwt_manager.create_access_token(
    data={"sub": "user123", "username": "john_doe"}
)
refresh_token = jwt_manager.create_refresh_token(
    data={"sub": "user123"}
)

# Verify tokens
try:
    payload = jwt_manager.verify_token(access_token)
    print(f"User: {payload.username}")
except jwt_manager.InvalidTokenError:
    print("Invalid token")
```

#### Configuration Options

```python
JWTConfig(
    secret_key="your-256-bit-secret",           # Required
    algorithm="HS256",                          # Default: HS256
    access_token_expire_minutes=30,             # Default: 30 minutes
    refresh_token_expire_days=7,                # Default: 7 days
    issuer="next-watch",                        # Optional
    audience="next-watch-api",                  # Optional
)
```

#### Integration with FastAPI

```python
from fastapi import FastAPI, Depends, HTTPException
from fast_core.security.jwt import create_jwt_manager
from fast_core.dependencies.auth import get_current_user

app = FastAPI()

@app.post("/login")
async def login(credentials: LoginCredentials):
    # Validate credentials
    user = await authenticate_user(credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create tokens
    access_token = jwt_manager.create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    refresh_token = jwt_manager.create_refresh_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/refresh")
async def refresh_token(refresh_token: str):
    try:
        payload = jwt_manager.verify_refresh_token(refresh_token)
        new_access_token = jwt_manager.create_access_token(
            data={"sub": payload.sub}
        )
        return {"access_token": new_access_token, "token_type": "bearer"}
    except jwt_manager.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.get("/protected")
async def protected_route(current_user = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}
```

### `rate_limit.py` - Rate Limiting

Provides flexible rate limiting with multiple backend implementations.

#### Key Classes

- `RateLimiter`: Abstract base class for rate limiters
- `MemoryRateLimiter`: In-memory rate limiting (single instance)
- `RedisRateLimiter`: Redis-based rate limiting (distributed)

#### Basic Usage

```python
from fast_core.security.rate_limit import (
    MemoryRateLimiter,
    RedisRateLimiter,
    rate_limit
)

# Memory-based rate limiter
memory_limiter = MemoryRateLimiter()

# Redis-based rate limiter
redis_limiter = RedisRateLimiter(redis_url="redis://localhost:6379")

# Use as decorator
@rate_limit(limiter=memory_limiter, max_requests=100, window_seconds=3600)
async def my_endpoint():
    return {"message": "Success"}
```

#### FastAPI Integration

```python
from fastapi import FastAPI, Request, HTTPException
from fast_core.security.rate_limit import check_rate_limit, get_client_key

app = FastAPI()

# Global rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_key = get_client_key(request)

    if not await check_rate_limit(
        limiter=redis_limiter,
        key=client_key,
        max_requests=1000,
        window_seconds=3600
    ):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": "3600"}
        )

    response = await call_next(request)
    return response

# Per-endpoint rate limiting
@app.get("/api/search")
@rate_limit(limiter=redis_limiter, max_requests=10, window_seconds=60)
async def search_endpoint(request: Request):
    return {"results": []}
```

#### Rate Limiting Strategies

1. **Per-IP Rate Limiting**:

```python
@rate_limit(
    limiter=redis_limiter,
    max_requests=100,
    window_seconds=3600,
    key_func=lambda request: request.client.host
)
```

2. **Per-User Rate Limiting**:

```python
def get_user_key(request: Request) -> str:
    # Extract user ID from JWT token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = jwt_manager.verify_token(token)
    return f"user:{payload.sub}"

@rate_limit(
    limiter=redis_limiter,
    max_requests=1000,
    window_seconds=3600,
    key_func=get_user_key
)
```

3. **Per-API-Key Rate Limiting**:

```python
def get_api_key(request: Request) -> str:
    return request.headers.get("X-API-Key", "anonymous")

@rate_limit(
    limiter=redis_limiter,
    max_requests=5000,
    window_seconds=3600,
    key_func=get_api_key
)
```

## Configuration

### JWT Configuration

JWT settings can be configured through environment variables:

```bash
# JWT Settings
JWT_SECRET_KEY=your-256-bit-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_ISSUER=next-watch
JWT_AUDIENCE=next-watch-api
```

### Rate Limiting Configuration

```bash
# Rate Limiting
REDIS_URL=redis://localhost:6379
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT_MAX_REQUESTS=1000
RATE_LIMIT_DEFAULT_WINDOW_SECONDS=3600
```

## Best Practices

### JWT Security

1. **Use strong secret keys**: Generate 256-bit random keys
2. **Short access token expiry**: 15-30 minutes maximum
3. **Longer refresh token expiry**: 7-30 days
4. **Include minimal claims**: Only include necessary user data
5. **Validate all claims**: Check issuer, audience, expiration

### Rate Limiting

1. **Choose appropriate limits**: Balance user experience with protection
2. **Use Redis for distributed systems**: Memory limiter only for single instances
3. **Implement graceful degradation**: Don't fail hard on rate limit errors
4. **Monitor rate limit metrics**: Track usage patterns
5. **Provide clear error messages**: Include retry-after headers

## Error Handling

Both JWT and rate limiting components provide comprehensive error handling:

### JWT Errors

```python
try:
    payload = jwt_manager.verify_token(token)
except jwt_manager.InvalidTokenError as e:
    # Handle invalid token (expired, malformed, etc.)
    raise HTTPException(status_code=401, detail=str(e))
except jwt_manager.ExpiredTokenError as e:
    # Handle expired token specifically
    raise HTTPException(status_code=401, detail="Token expired")
```

### Rate Limiting Errors

```python
if not await check_rate_limit(limiter, key, max_requests, window):
    raise HTTPException(
        status_code=429,
        detail="Rate limit exceeded",
        headers={
            "Retry-After": str(window),
            "X-RateLimit-Limit": str(max_requests),
            "X-RateLimit-Window": str(window)
        }
    )
```

## Testing

### JWT Testing

```python
import pytest
from fast_core.security.jwt import create_jwt_manager, JWTConfig

@pytest.fixture
def jwt_manager():
    config = JWTConfig(secret_key="test-secret-key")
    return create_jwt_manager(config)

def test_token_creation(jwt_manager):
    token = jwt_manager.create_access_token({"sub": "test_user"})
    assert token is not None

    payload = jwt_manager.verify_token(token)
    assert payload.sub == "test_user"
```

### Rate Limiting Testing

```python
import pytest
from fast_core.security.rate_limit import MemoryRateLimiter

@pytest.fixture
def rate_limiter():
    return MemoryRateLimiter()

@pytest.mark.asyncio
async def test_rate_limiting(rate_limiter):
    # Should allow first request
    allowed = await rate_limiter.check_rate_limit("test_key", 1, 60)
    assert allowed is True

    # Should block second request
    allowed = await rate_limiter.check_rate_limit("test_key", 1, 60)
    assert allowed is False
```

## Integration with Next Watch Services

The security module integrates seamlessly with:

- **Auth API**: JWT token validation and user authentication
- **BFF API**: Rate limiting for client requests
- **Backend API**: Service-to-service authentication
- **Config Library**: Environment-based configuration
- **Cache Library**: Redis backend for distributed rate limiting
