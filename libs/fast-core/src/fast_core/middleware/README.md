# Fast Core Middleware System

The Fast Core Middleware System provides a comprehensive, production-ready middleware stack for FastAPI applications with a flexible builder pattern, automatic configuration, and enterprise-grade features.

## 📁 Module Overview

### Core Components

| Module                       | Purpose                                   | Key Features                                             |
| ---------------------------- | ----------------------------------------- | -------------------------------------------------------- |
| [`config.py`](./config.py)   | Configuration classes and builder pattern | MiddlewareConfig builder, dataclass configs, type safety |
| [`setup.py`](./setup.py)     | Middleware orchestration and setup        | Automatic middleware ordering, environment detection     |
| [`context.py`](./context.py) | Request context and distributed tracing   | W3C/B3/Jaeger propagation, request correlation           |
| [`tracing.py`](./tracing.py) | OpenTelemetry infrastructure setup        | Auto-instrumentation, trace exporters, service metadata  |

### Specialized Middleware

| Module                         | Purpose                         | Production Features                                |
| ------------------------------ | ------------------------------- | -------------------------------------------------- |
| [`cors.py`](./cors.py)         | Cross-Origin Resource Sharing   | Environment-aware origins, security validation     |
| [`security.py`](./security.py) | Security headers and protection | HSTS, CSP, frame protection, trusted hosts         |
| [`logging.py`](./logging.py)   | Request/response logging        | Structured logging, sensitive data masking         |
| [`metrics.py`](./metrics.py)   | Prometheus metrics collection   | HTTP metrics, custom buckets, performance tracking |

## 🏗️ Architecture

```mermaid
graph TD
    A[FastAPI Application] --> B[create_app]
    B --> C[setup_tracing - OpenTelemetry Infrastructure]
    B --> D[setup_middleware - Request Processing Stack]

    C --> E[Service Instrumentation]
    C --> F[Trace Exporters]
    C --> G[Propagation Context]

    D --> H[Middleware Builder Config]
    H --> I[CORS - Outermost]
    I --> J[Security Headers]
    J --> K[Rate Limiting]
    K --> L[Logging]
    L --> M[Metrics]
    M --> N[Request Processing]
    N --> O[Context - Innermost]

    O --> P[Your Route Handlers]
```

## 🚀 Quick Start

### Basic Usage

```python
from fast_core.middleware import MiddlewareConfig
from fast_core import create_app

# Simple configuration
middleware = MiddlewareConfig()
middleware.cors(
    origins=["http://localhost:3000"],
    credentials=True
).request_processing(
    include_request_id=True,
    gzip_compression=True
)

app = create_app(middleware=middleware)
```

### Production Configuration

```python
middleware = MiddlewareConfig()

# Production CORS (strict)
middleware.cors(
    origins=["https://app.example.com", "https://mobile.example.com"],
    credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    headers=["Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
    max_age=3600
)

# Security headers (comprehensive)
.security_headers(
    hsts=True,
    hsts_max_age=63072000,  # 2 years
    hsts_include_subdomains=True,
    frame_options="DENY",
    content_type_options=True,
    xss_protection=True,
    csp="default-src 'self'; connect-src 'self' https://api.example.com",
    referrer_policy="strict-origin-when-cross-origin",
    trusted_hosts=["app.example.com"]
)

# Rate limiting (endpoint-specific)
.rate_limiting(
    default_limit="1000/hour",
    endpoints={
        "/api/auth/login": "10/minute",
        "/api/auth/register": "5/minute",
        "/api/upload": "20/minute"
    },
    exempt_ips=["10.0.0.0/8"],
    headers=False  # Don't expose limits in production
)

# Logging (minimal in production)
.logging(
    level="INFO",
    include_request_body=False,
    include_response_body=False,
    exclude_headers=["authorization", "cookie"],
    log_timing=True
)

# Request processing
.request_processing(
    max_request_size=10 * 1024 * 1024,
    timeout=30,
    include_request_id=True,
    gzip_compression=True
)

# Metrics (always enabled)
.metrics(
    track_request_size=True,
    track_response_size=True,
    custom_buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)
```

## 🔧 Module Documentation

### Configuration System (`config.py`)

The heart of the middleware system, providing type-safe configuration classes and a fluent builder pattern.

**Key Classes:**

- `MiddlewareConfig` - Main builder class with method chaining
- `CORSConfig` - CORS-specific configuration
- `SecurityConfig` - Security headers configuration
- `LoggingConfig` - Request/response logging settings
- `RateLimitConfig` - Rate limiting rules and exemptions
- `RequestConfig` - Request processing settings
- `MetricsConfig` - Prometheus metrics configuration
- `ContextConfig` - Request context and tracing settings

**Example:**

```python
# All configurations are strongly typed
config = MiddlewareConfig()
config.cors(origins=["https://example.com"])  # List[str]
config.security_headers(hsts_max_age=31536000)  # int
config.rate_limiting(enabled=True)  # bool
```

### Setup and Orchestration (`setup.py`)

Handles the automatic setup and ordering of middleware components.

**Key Features:**

- **Automatic ordering** - Middleware added in correct sequence
- **Environment detection** - Auto-enables tracing context when available
- **Graceful degradation** - Missing dependencies don't break the stack
- **Performance optimization** - Efficient middleware chain

**Middleware Order (outer to inner):**

1. CORS (Cross-Origin Resource Sharing)
2. Security Headers (HSTS, CSP, Frame Protection)
3. Rate Limiting (Request throttling)
4. Logging (Request/response logging)
5. Metrics (Prometheus collection)
6. Request Processing (Timeouts, compression)
7. Context (Request correlation, tracing)

### Request Context and Tracing (`context.py`)

Provides distributed tracing context propagation and request correlation across services.

**Key Features:**

- **Multi-format support** - W3C Trace Context, B3 (Zipkin), Jaeger
- **Automatic propagation** - Headers injected into downstream calls
- **Request correlation** - Request IDs for debugging
- **User context** - User ID extraction from JWT tokens
- **OpenTelemetry integration** - Automatic span attributes

**Usage:**

```python
from fast_core.middleware.context import get_request_id, get_trace_headers

# In your route handlers
async def my_handler():
    request_id = get_request_id()
    trace_headers = get_trace_headers()
    # Headers automatically include trace context for downstream calls
```

### OpenTelemetry Infrastructure (`tracing.py`)

Sets up the foundational OpenTelemetry instrumentation for the entire application.

**Key Features:**

- **Auto-instrumentation** - FastAPI, HTTPx, SQLAlchemy, Redis
- **Trace exporters** - Configurable exporters (OTLP, Jaeger, Console)
- **Service metadata** - Automatic service name, version, environment
- **Resource attributes** - Container, host, deployment information
- **Propagation setup** - Distributed trace correlation

**Automatic Instrumentation:**

- FastAPI requests and responses
- HTTPx client requests (service-to-service)
- SQLAlchemy database queries
- Redis operations
- Custom application spans

### Cross-Origin Resource Sharing (`cors.py`)

Handles CORS configuration with environment-aware security.

**Features:**

- **Environment-specific origins** - Different origins for dev/prod
- **Security validation** - Prevents wildcard origins in production
- **Credential handling** - Configurable credential support
- **Method/header control** - Fine-grained access control

### Security Headers (`security.py`)

Comprehensive security header management for production applications.

**Security Features:**

- **HSTS** - HTTP Strict Transport Security
- **CSP** - Content Security Policy
- **Frame protection** - X-Frame-Options
- **Content type sniffing protection**
- **XSS protection**
- **Referrer policy**
- **Trusted host validation**

### Request/Response Logging (`logging.py`)

Structured logging with sensitive data protection and performance optimization.

**Features:**

- **Structured logging** - JSON format with consistent fields
- **Sensitive data masking** - Automatic header/body sanitization
- **Performance tracking** - Request timing and size metrics
- **Configurable verbosity** - Environment-specific log levels
- **Path exclusion** - Skip logging for health checks

### Metrics Collection (`metrics.py`)

Prometheus metrics integration for observability and monitoring.

**Metrics:**

- **HTTP request metrics** - Duration, status codes, methods
- **Request/response sizes** - Payload size tracking
- **Custom buckets** - Configurable histogram buckets
- **Endpoint labeling** - Per-route metrics
- **Performance histograms** - Response time distributions

## 🔄 Integration Patterns

### Automatic Setup

Fast Core automatically configures middleware when tracing is enabled:

```python
# In your service configuration
fast_core_config = FastAPIConfig(
    service_name="my-service",
    enable_tracing=True  # This triggers automatic context middleware
)

# Context middleware is automatically added with optimal settings
app = create_app(settings=fast_core_config)
```

### Manual Configuration

For fine-grained control, use the builder pattern:

```python
middleware = MiddlewareConfig()

# Environment-specific configuration
if config.is_production:
    middleware.cors(origins=config.cors_origins)
    middleware.security_headers(hsts=True, csp=production_csp)
else:
    middleware.cors(origins=["*"])
    middleware.logging(level="DEBUG", include_request_body=True)

# Common configuration
middleware.request_processing(include_request_id=True)
middleware.metrics(enabled=True)
```

### Service-to-Service Integration

The middleware automatically handles service-to-service communication:

```python
# Headers are automatically injected with trace context
async def call_backend_service():
    # get_trace_headers() provides W3C/B3/Jaeger headers
    headers = get_trace_headers()
    response = await httpx.get("http://backend/api", headers=headers)
    return response
```

## 🛡️ Production Best Practices

### Security Configuration

```python
# Production security checklist
middleware.security_headers(
    hsts=True,                    # ✅ Force HTTPS
    hsts_max_age=63072000,       # ✅ 2 year HSTS
    hsts_include_subdomains=True, # ✅ Include subdomains
    frame_options="DENY",         # ✅ Prevent clickjacking
    content_type_options=True,    # ✅ Prevent MIME sniffing
    xss_protection=True,          # ✅ XSS protection
    csp="default-src 'self'",     # ✅ Content Security Policy
    trusted_hosts=["yourdomain.com"]  # ✅ Host validation
)
```

### Performance Configuration

```python
# Performance optimizations
middleware.request_processing(
    gzip_compression=True,        # ✅ Compress responses
    gzip_minimum_size=1000,      # ✅ Only compress larger responses
    timeout=30,                   # ✅ Reasonable timeout
    max_request_size=10_000_000  # ✅ 10MB limit
)

middleware.logging(
    include_request_body=False,   # ✅ Don't log bodies in prod
    include_response_body=False,  # ✅ Reduce log volume
    exclude_paths=["/health"]     # ✅ Skip health checks
)
```

### Monitoring Configuration

```python
# Comprehensive observability
middleware.metrics(
    track_request_size=True,      # ✅ Monitor payload sizes
    track_response_size=True,     # ✅ Monitor response sizes
    custom_buckets=[              # ✅ SLA-aligned buckets
        0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0
    ],
    exclude_paths=["/metrics"]    # ✅ Don't track metrics endpoint
)

# Automatic tracing context
# ✅ No configuration needed - automatically enabled
```

## 🧪 Testing

### Unit Testing

```python
def test_middleware_config():
    config = MiddlewareConfig()
    config.cors(origins=["https://example.com"])

    assert config.cors_config.origins == ["https://example.com"]
    assert config.cors_config.enabled is True
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_middleware_stack():
    middleware = MiddlewareConfig()
    middleware.cors(origins=["*"]).request_processing(include_request_id=True)

    app = create_app(middleware=middleware)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert "x-request-id" in response.headers
```

## 📊 Monitoring and Observability

### Metrics Endpoints

- `/metrics` - Prometheus metrics
- `/health` - Health check endpoint
- `/meta` - Service metadata

### Trace Correlation

All requests automatically include:

- Request ID for correlation
- Trace headers for distributed tracing
- User context for personalization
- Service metadata for routing

### Log Structure

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "info",
  "logger": "fast_core.middleware",
  "event": "request_completed",
  "request_id": "req-123",
  "trace_id": "trace-456",
  "method": "GET",
  "path": "/api/users",
  "status_code": 200,
  "duration_ms": 45.2,
  "user_id": "user-789"
}
```

## 🔧 Troubleshooting

### Common Issues

**CORS Issues:**

```python
# ❌ Wildcard origins in production
middleware.cors(origins=["*"])  # Security risk

# ✅ Explicit origins in production
middleware.cors(origins=["https://yourdomain.com"])
```

**Rate Limiting:**

```python
# ❌ No Redis configuration
middleware.rate_limiting(default_limit="100/minute")  # Uses memory

# ✅ Redis for distributed rate limiting
middleware.rate_limiting(
    default_limit="100/minute",
    storage_url="redis://localhost:6379/0"
)
```

**Logging Performance:**

```python
# ❌ Verbose logging in production
middleware.logging(include_request_body=True)  # Performance impact

# ✅ Minimal logging in production
middleware.logging(include_request_body=False, level="INFO")
```

### Debugging

Enable debug logging to see middleware setup:

```python
import logging
logging.getLogger("fast_core.middleware").setLevel(logging.DEBUG)
```

## 🎯 Migration Guide

### From Legacy FastAPI

```python
# Old way - manual middleware setup
app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)

# New way - builder pattern
middleware = MiddlewareConfig()
middleware.cors(origins=["*"]).request_processing(gzip_compression=True)
app = create_app(middleware=middleware)
```

### From Other Frameworks

```python
# Flask equivalent
middleware.cors(origins=["*"])
middleware.security_headers(hsts=True)
middleware.logging(level="INFO")

# Express equivalent
middleware.cors(credentials=True)
middleware.request_processing(max_request_size=10_000_000)
middleware.rate_limiting(default_limit="100/minute")
```

---

**Fast Core Middleware System** - Production-ready, type-safe, and highly configurable middleware for modern FastAPI applications.
