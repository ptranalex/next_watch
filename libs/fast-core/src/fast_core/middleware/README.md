***REMOVED*** Middleware Module

The middleware module provides essential middleware components for FastAPI applications. These middleware handle cross-cutting concerns like CORS, logging, security headers, rate limiting, metrics, and tracing across Next Watch services.

***REMOVED******REMOVED*** Overview

This module contains middleware for:

- **CORS**: Cross-Origin Resource Sharing configuration
- **Logging**: Request/response logging with timing and context
- **Security**: Security headers, rate limiting, and trusted hosts
- **Metrics**: Request metrics collection (placeholder)
- **Tracing**: Distributed tracing support (placeholder)

***REMOVED******REMOVED*** Module Structure

***REMOVED******REMOVED******REMOVED*** `cors.py` - CORS Middleware

Handles Cross-Origin Resource Sharing with production and development configurations.

***REMOVED******REMOVED******REMOVED******REMOVED*** Basic Usage

```python
from fastapi import FastAPI
from fast_core.middleware.cors import setup_cors, setup_production_cors

app = FastAPI()

***REMOVED*** Development CORS (permissive)
setup_cors(app)

***REMOVED*** Production CORS (restrictive)
setup_production_cors(app, allowed_origins=["https://example.com"])
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Configuration Options

```python
from fast_core.middleware.cors import get_default_cors_config

***REMOVED*** Get default configuration
cors_config = get_default_cors_config()

***REMOVED*** Custom configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Environment-Based Setup

```python
import os
from fast_core.middleware.cors import setup_cors, setup_production_cors

if os.getenv("ENVIRONMENT") == "production":
    setup_production_cors(
        app,
        allowed_origins=os.getenv("CORS_ORIGINS", "").split(",")
    )
else:
    setup_cors(app)
```

***REMOVED******REMOVED******REMOVED*** `logging.py` - Request Logging Middleware

Provides comprehensive request/response logging with timing, context, and structured data.

***REMOVED******REMOVED******REMOVED******REMOVED*** Features

- Request/response timing
- Request ID generation and tracking
- Structured logging with context
- Configurable log levels
- Error logging integration

***REMOVED******REMOVED******REMOVED******REMOVED*** Basic Usage

```python
from fastapi import FastAPI
from fast_core.middleware.logging import setup_logging, LoggingMiddleware

app = FastAPI()

***REMOVED*** Simple setup
setup_logging(app)

***REMOVED*** Custom setup
app.add_middleware(
    LoggingMiddleware,
    logger_name="my-api",
    log_level="INFO",
    include_request_body=True,
    include_response_body=False,
)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Request Logger Access

```python
from fast_core.middleware.logging import get_request_logger

@app.get("/users")
async def get_users(request: Request):
    logger = get_request_logger(request)
    logger.info("Fetching users", extra={"user_count": 100})
    return {"users": []}
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Log Format

The middleware produces structured logs:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Request completed",
  "request_id": "req-abc123",
  "method": "GET",
  "path": "/api/users",
  "status_code": 200,
  "duration_ms": 45.2,
  "client_ip": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "response_size": 1024
}
```

***REMOVED******REMOVED******REMOVED*** `security.py` - Security Middleware

Provides security headers, rate limiting, and trusted host validation.

***REMOVED******REMOVED******REMOVED******REMOVED*** Components

- `SecurityHeadersMiddleware`: Adds security headers
- `RateLimitMiddleware`: Request rate limiting
- Trusted host validation

***REMOVED******REMOVED******REMOVED******REMOVED*** Security Headers

```python
from fast_core.middleware.security import setup_security, get_security_headers

app = FastAPI()

***REMOVED*** Setup all security middleware
setup_security(app)

***REMOVED*** Custom security headers
headers = get_security_headers(
    hsts_max_age=31536000,
    content_type_options=True,
    frame_options="DENY",
    xss_protection=True
)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Default Security Headers

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Rate Limiting Integration

```python
from fast_core.middleware.security import RateLimitMiddleware
from fast_core.security.rate_limit import RedisRateLimiter

rate_limiter = RedisRateLimiter(redis_url="redis://localhost:6379")

app.add_middleware(
    RateLimitMiddleware,
    rate_limiter=rate_limiter,
    max_requests=1000,
    window_seconds=3600,
    key_func=lambda request: request.client.host
)
```

***REMOVED******REMOVED******REMOVED*** `metrics.py` - Metrics Middleware (Placeholder)

Placeholder for request metrics collection.

```python
from fast_core.middleware.metrics import setup_metrics

app = FastAPI()
setup_metrics(app)
```

***REMOVED******REMOVED******REMOVED*** `tracing.py` - Tracing Middleware (Placeholder)

Placeholder for distributed tracing integration.

```python
from fast_core.middleware.tracing import setup_tracing

app = FastAPI()
setup_tracing(app)
```

***REMOVED******REMOVED*** Complete Middleware Setup

***REMOVED******REMOVED******REMOVED*** Basic Setup

```python
from fastapi import FastAPI
from fast_core.middleware import setup_middleware

app = FastAPI()

***REMOVED*** Setup all middleware with defaults
setup_middleware(app)
```

***REMOVED******REMOVED******REMOVED*** Custom Setup

```python
from fastapi import FastAPI
from fast_core.middleware import (
    setup_cors,
    setup_logging,
    setup_security
)

app = FastAPI()

***REMOVED*** Setup individual middleware
setup_cors(app)
setup_logging(app, log_level="DEBUG")
setup_security(app)
```

***REMOVED******REMOVED******REMOVED*** Production Setup

```python
import os
from fastapi import FastAPI
from fast_core.middleware import (
    setup_production_cors,
    setup_logging,
    setup_security
)

app = FastAPI()

***REMOVED*** Production-ready middleware
setup_production_cors(
    app,
    allowed_origins=os.getenv("CORS_ORIGINS", "").split(",")
)
setup_logging(
    app,
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    include_request_body=False  ***REMOVED*** Don't log request bodies in production
)
setup_security(app)
```

***REMOVED******REMOVED*** Configuration

Middleware can be configured through environment variables:

```bash
***REMOVED*** CORS Configuration
CORS_ORIGINS=https://example.com,https://app.example.com
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE
CORS_ALLOW_HEADERS=*

***REMOVED*** Logging Configuration
LOG_LEVEL=INFO
LOG_INCLUDE_REQUEST_BODY=false
LOG_INCLUDE_RESPONSE_BODY=false
LOG_MAX_BODY_SIZE=1024

***REMOVED*** Security Configuration
SECURITY_HSTS_MAX_AGE=31536000
SECURITY_FRAME_OPTIONS=DENY
SECURITY_CONTENT_TYPE_OPTIONS=true
SECURITY_XSS_PROTECTION=true

***REMOVED*** Rate Limiting
RATE_LIMIT_MAX_REQUESTS=1000
RATE_LIMIT_WINDOW_SECONDS=3600
RATE_LIMIT_REDIS_URL=redis://localhost:6379
```

***REMOVED******REMOVED*** Middleware Order

Middleware order is important. The recommended order is:

1. **CORS Middleware** - Handle preflight requests first
2. **Security Headers** - Add security headers early
3. **Rate Limiting** - Block requests before processing
4. **Logging Middleware** - Log all requests and responses
5. **Metrics/Tracing** - Collect performance data
6. **Application Routes** - Your actual application logic

```python
from fastapi import FastAPI
from fast_core.middleware import (
    setup_cors,
    setup_security,
    setup_logging
)

app = FastAPI()

***REMOVED*** Order matters!
setup_cors(app)          ***REMOVED*** 1. CORS first
setup_security(app)      ***REMOVED*** 2. Security headers
setup_logging(app)       ***REMOVED*** 3. Logging last (to capture everything)
```

***REMOVED******REMOVED*** Best Practices

***REMOVED******REMOVED******REMOVED*** CORS Configuration

1. **Production**: Always specify exact origins, never use `*`
2. **Development**: Use `*` for convenience but not in production
3. **Credentials**: Only allow credentials with specific origins
4. **Headers**: Expose necessary headers like `X-Request-ID`

***REMOVED******REMOVED******REMOVED*** Logging

1. **Sensitive Data**: Never log passwords, tokens, or personal data
2. **Request Bodies**: Disable in production to avoid logging sensitive data
3. **Log Levels**: Use appropriate levels (DEBUG for development, INFO/WARNING for production)
4. **Structured Logging**: Always use structured JSON logs

***REMOVED******REMOVED******REMOVED*** Security

1. **HTTPS Only**: Always use HTTPS in production
2. **Security Headers**: Enable all security headers
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Trusted Hosts**: Validate Host headers to prevent host header injection

***REMOVED******REMOVED*** Testing

***REMOVED******REMOVED******REMOVED*** CORS Testing

```python
from fastapi.testclient import TestClient

def test_cors_headers(client: TestClient):
    response = client.options("/api/users", headers={
        "Origin": "https://example.com",
        "Access-Control-Request-Method": "GET"
    })

    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
```

***REMOVED******REMOVED******REMOVED*** Logging Testing

```python
import logging
from fastapi.testclient import TestClient

def test_request_logging(client: TestClient, caplog):
    with caplog.at_level(logging.INFO):
        response = client.get("/api/users")

    assert response.status_code == 200
    assert "Request completed" in caplog.text
    assert "GET /api/users" in caplog.text
```

***REMOVED******REMOVED******REMOVED*** Security Testing

```python
def test_security_headers(client: TestClient):
    response = client.get("/api/users")

    assert "X-Content-Type-Options" in response.headers
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
```

***REMOVED******REMOVED*** Integration with Next Watch Services

The middleware module integrates with:

- **Config Library**: Environment-based configuration
- **CLI Library**: Structured logging integration
- **Cache Library**: Redis backend for rate limiting
- **Security Module**: JWT validation and rate limiting
- **All APIs**: Consistent middleware across services

***REMOVED******REMOVED*** Performance Considerations

1. **Middleware Order**: Place expensive middleware last
2. **Rate Limiting**: Use Redis for distributed systems
3. **Logging**: Avoid logging large request/response bodies
4. **Security Headers**: Minimal performance impact
5. **CORS**: Preflight requests add latency for complex requests

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Common Issues

1. **CORS Errors**: Check origin configuration and preflight handling
2. **Rate Limit False Positives**: Verify client key extraction logic
3. **Missing Request IDs**: Ensure logging middleware is properly configured
4. **Security Header Conflicts**: Check for duplicate middleware registration
