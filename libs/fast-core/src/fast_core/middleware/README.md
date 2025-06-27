***REMOVED*** Fast Core Middleware Builder

The Fast Core Middleware Builder provides a flexible, granular approach to configuring FastAPI middleware with a clean builder pattern interface. This system replaces the all-or-nothing middleware approach with fine-grained control over individual middleware components.

***REMOVED******REMOVED*** Features

- **Builder Pattern**: Fluent interface for chaining middleware configurations
- **Granular Control**: Configure each middleware type independently
- **Type Safety**: Full type annotations and IDE support
- **Backward Compatibility**: Works alongside existing AppOptions system
- **Production Ready**: Comprehensive middleware implementations

***REMOVED******REMOVED*** Middleware Types

***REMOVED******REMOVED******REMOVED*** 1. CORS Middleware

Configure Cross-Origin Resource Sharing with specific origins, methods, and headers.

```python
middleware.cors(
    origins=["https://app.example.com", "https://mobile.example.com"],
    credentials=True,
    methods=["GET", "POST", "PUT", "DELETE"],
    headers=["Content-Type", "Authorization"],
    expose_headers=["X-Request-ID"],
    max_age=3600
)
```

***REMOVED******REMOVED******REMOVED*** 2. Security Headers Middleware

Add comprehensive security headers to protect your application.

```python
middleware.security_headers(
    hsts=True,
    hsts_max_age=31536000,  ***REMOVED*** 1 year
    frame_options="DENY",
    content_type_options=True,
    xss_protection=True,
    csp="default-src 'self'; script-src 'self' 'unsafe-inline'",
    referrer_policy="strict-origin-when-cross-origin",
    trusted_hosts=["app.example.com"]
)
```

***REMOVED******REMOVED******REMOVED*** 3. Rate Limiting Middleware

Implement rate limiting with per-endpoint rules and IP exemptions.

```python
middleware.rate_limiting(
    default_limit="100/minute",
    storage_url="redis://localhost:6379/0",  ***REMOVED*** For distributed rate limiting
    endpoints={
        "/api/auth/login": "5/minute",
        "/api/auth/register": "3/minute",
        "/api/upload": "10/minute"
    },
    exempt_ips=["127.0.0.1", "10.0.0.0/8"],
    headers=True  ***REMOVED*** Include rate limit headers in responses
)
```

***REMOVED******REMOVED******REMOVED*** 4. Request Logging Middleware

Log requests and responses with configurable detail levels.

```python
middleware.logging(
    level="INFO",
    include_request_body=False,  ***REMOVED*** Be careful in production
    include_response_body=False,
    max_body_size=1024,
    exclude_paths=["/health", "/metrics"],
    include_headers=True,
    exclude_headers=["authorization", "cookie"],
    log_timing=True,
    log_user_agent=True
)
```

***REMOVED******REMOVED******REMOVED*** 5. Request Processing Middleware

Handle request IDs, process timing, compression, and size limits.

```python
middleware.request_processing(
    max_request_size=5 * 1024 * 1024,  ***REMOVED*** 5MB
    timeout=30,
    include_request_id=True,
    request_id_header="X-Request-ID",
    include_process_time=True,
    process_time_header="X-Process-Time",
    gzip_compression=True,
    gzip_minimum_size=1000
)
```

***REMOVED******REMOVED******REMOVED*** 6. Metrics Middleware (NEW!)

Comprehensive Prometheus metrics collection for monitoring and observability.

```python
middleware.metrics(
    endpoint_path="/metrics",
    include_endpoint=True,
    exclude_paths=["/health", "/metrics", "/docs"],
    exclude_methods=["OPTIONS"],
    custom_buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    track_request_size=True,
    track_response_size=True
)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Collected Metrics

The metrics middleware automatically collects:

- **`http_requests_total`**: Total HTTP requests by method, endpoint, status code, service
- **`http_request_duration_seconds`**: Request duration histogram with configurable buckets
- **`http_requests_in_progress`**: Current requests being processed
- **`http_request_size_bytes`**: Request payload size distribution
- **`http_response_size_bytes`**: Response payload size distribution
- **`service_info`**: Service metadata (name, version)

***REMOVED******REMOVED******REMOVED******REMOVED*** Custom Metrics

You can also create custom metrics using the metrics registry:

```python
from fast_core.monitoring.metrics import get_metrics_registry, track_operation

***REMOVED*** Get the metrics registry
metrics = get_metrics_registry()

***REMOVED*** Create custom metrics
user_registrations = metrics.create_counter(
    "user_registrations_total",
    "Total user registrations",
    ["registration_type", "source"]
)

cache_hits = metrics.create_counter(
    "cache_operations_total",
    "Cache operations",
    ["operation", "result"]
)

recommendation_quality = metrics.create_histogram(
    "recommendation_quality_score",
    "Quality score of recommendations",
    ["algorithm", "user_segment"],
    buckets=[0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0]
)

***REMOVED*** Use in your code
user_registrations.labels(registration_type="email", source="web").inc()
cache_hits.labels(operation="get", result="hit").inc()
recommendation_quality.labels(algorithm="collaborative", user_segment="active").observe(0.85)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Operation Tracking

Track custom operations with automatic timing and error handling:

```python
from fast_core.monitoring.metrics import track_operation

@track_operation(metrics, "user_authentication", {"method": "jwt"})
async def authenticate_user(token: str) -> User:
    ***REMOVED*** Automatically tracked:
    ***REMOVED*** - operation_duration_seconds{operation="user_authentication", method="jwt", status="success"}
    ***REMOVED*** - operation_total{operation="user_authentication", method="jwt", status="success"}
    return await validate_jwt_token(token)

@track_operation(metrics, "database_query", {"table": "movies"})
async def get_movies(limit: int) -> List[Movie]:
    ***REMOVED*** Metrics collected automatically on success/failure
    return await db.query("SELECT * FROM movies LIMIT ?", limit)
```

***REMOVED******REMOVED*** Usage Examples

***REMOVED******REMOVED******REMOVED*** Basic Configuration

```python
from fast_core.app import create_app
from fast_core.middleware import MiddlewareConfig

***REMOVED*** Create middleware configuration
middleware = MiddlewareConfig()
middleware.cors(
    origins=["http://localhost:3000"],
    credentials=True
).request_processing(
    include_request_id=True,
    include_process_time=True
).metrics(
    custom_buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    exclude_paths=["/health", "/metrics"]
)

***REMOVED*** Create app with middleware
app = create_app(
    settings=settings,
    middleware=middleware,
    routers=[api_router]
)
```

***REMOVED******REMOVED******REMOVED*** Production Configuration

```python
***REMOVED*** Production-ready middleware stack
middleware = MiddlewareConfig()
middleware.cors(
    origins=[
        "https://app.example.com",
        "https://mobile.example.com"
    ],
    credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    headers=["Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["X-Request-ID", "X-Process-Time"]
).security_headers(
    hsts=True,
    hsts_max_age=63072000,  ***REMOVED*** 2 years
    hsts_include_subdomains=True,
    frame_options="DENY",
    content_type_options=True,
    xss_protection=True,
    csp="default-src 'self'; connect-src 'self' https://api.example.com",
    referrer_policy="strict-origin-when-cross-origin",
    trusted_hosts=["app.example.com", "api.example.com"]
).rate_limiting(
    default_limit="1000/hour",
    storage_url="redis://localhost:6379/0",
    endpoints={
        "/api/auth/login": "10/minute",
        "/api/auth/refresh": "20/minute",
        "/api/upload": "5/minute"
    },
    exempt_ips=["10.0.0.0/8", "192.168.0.0/16"]
).logging(
    level="INFO",
    include_request_body=False,
    include_response_body=False,
    exclude_paths=["/health", "/metrics", "/favicon.ico"],
    include_headers=True,
    exclude_headers=["authorization", "cookie", "x-api-key"],
    log_timing=True,
    log_user_agent=False
).request_processing(
    max_request_size=5 * 1024 * 1024,
    timeout=30,
    include_request_id=True,
    include_process_time=True,
    gzip_compression=True,
    gzip_minimum_size=1000
)

app = create_app(settings=settings, middleware=middleware)
```

***REMOVED******REMOVED******REMOVED*** Development Configuration

```python
***REMOVED*** Development-friendly configuration
middleware = MiddlewareConfig()
middleware.cors(
    origins=["*"],  ***REMOVED*** Allow all origins in development
    credentials=False
).logging(
    level="DEBUG",
    include_request_body=True,
    include_response_body=True,
    max_body_size=2048,
    exclude_paths=["/health"],
    log_timing=True,
    log_user_agent=True
).request_processing(
    include_request_id=True,
    include_process_time=True,
    gzip_compression=True
).metrics(
    custom_buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    exclude_paths=["/health", "/metrics", "/docs"],
    track_request_size=True,
    track_response_size=True
)

app = create_app(settings=settings, middleware=middleware)
```

***REMOVED******REMOVED******REMOVED*** Security-Focused Configuration

```python
***REMOVED*** Security-focused configuration
middleware = MiddlewareConfig()
middleware.cors(
    origins=["https://secure-app.example.com"],
    credentials=True,
    methods=["GET", "POST", "PUT", "DELETE"]
).security_headers(
    hsts=True,
    hsts_max_age=31536000,
    frame_options="DENY",
    csp="default-src 'self'; script-src 'self' 'unsafe-inline'",
    trusted_hosts=["secure-app.example.com", "api.example.com"]
).rate_limiting(
    default_limit="100/minute",
    endpoints={
        "/api/auth/login": "5/minute",
        "/api/auth/register": "3/minute"
    },
    exempt_ips=["127.0.0.1"]
)

app = create_app(settings=settings, middleware=middleware)
```

***REMOVED******REMOVED*** Migration from AppOptions

***REMOVED******REMOVED******REMOVED*** Before (Legacy)

```python
from fast_core.app import create_app, AppOptions

app = create_app(
    settings=settings,
    options=AppOptions(
        middleware=True,
        cors=True,
        docs=True
    )
)
```

***REMOVED******REMOVED******REMOVED*** After (New System)

```python
from fast_core.app import create_app
from fast_core.middleware import MiddlewareConfig

middleware = MiddlewareConfig()
middleware.cors().request_processing()

app = create_app(
    settings=settings,
    middleware=middleware  ***REMOVED*** Takes precedence over options
)
```

***REMOVED******REMOVED******REMOVED*** Backward Compatibility

The new system is fully backward compatible. You can use both systems simultaneously:

```python
***REMOVED*** This works - middleware takes precedence
app = create_app(
    settings=settings,
    options=AppOptions(middleware=True),  ***REMOVED*** Fallback
    middleware=middleware_config  ***REMOVED*** Primary
)
```

***REMOVED******REMOVED*** Configuration Reference

***REMOVED******REMOVED******REMOVED*** CORSConfig

- `enabled: bool = True` - Enable/disable CORS middleware
- `origins: List[str] = ["*"]` - Allowed origins
- `methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]` - Allowed methods
- `headers: List[str] = ["*"]` - Allowed headers
- `credentials: bool = False` - Allow credentials
- `expose_headers: List[str] = []` - Headers to expose to client
- `max_age: int = 600` - Cache duration for preflight requests

***REMOVED******REMOVED******REMOVED*** SecurityConfig

- `enabled: bool = True` - Enable/disable security headers
- `hsts: bool = True` - Enable HTTP Strict Transport Security
- `hsts_max_age: int = 31536000` - HSTS max age in seconds
- `hsts_include_subdomains: bool = True` - Include subdomains in HSTS
- `frame_options: str = "DENY"` - X-Frame-Options header value
- `content_type_options: bool = True` - Enable X-Content-Type-Options: nosniff
- `xss_protection: bool = True` - Enable X-XSS-Protection
- `csp: Optional[str] = None` - Content Security Policy header value
- `referrer_policy: str = "strict-origin-when-cross-origin"` - Referrer-Policy header
- `trusted_hosts: List[str] = []` - List of trusted host patterns

***REMOVED******REMOVED******REMOVED*** LoggingConfig

- `enabled: bool = True` - Enable/disable logging middleware
- `level: str = "INFO"` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `include_request_body: bool = False` - Whether to log request bodies
- `include_response_body: bool = False` - Whether to log response bodies
- `max_body_size: int = 1024` - Maximum body size to log in bytes
- `exclude_paths: List[str] = ["/health", "/metrics"]` - Paths to exclude from logging
- `include_headers: bool = True` - Whether to log headers
- `exclude_headers: List[str] = ["authorization", "cookie"]` - Headers to exclude
- `log_timing: bool = True` - Whether to log request timing
- `log_user_agent: bool = True` - Whether to log user agent

***REMOVED******REMOVED******REMOVED*** RateLimitConfig

- `enabled: bool = True` - Enable/disable rate limiting
- `default_limit: str = "100/minute"` - Default rate limit (format: "requests/period")
- `storage_url: Optional[str] = None` - Redis URL for distributed rate limiting
- `key_func: str = "ip"` - Key function for rate limiting ("ip", "user", or custom)
- `endpoints: Dict[str, str] = {}` - Per-endpoint rate limits {"/path": "limit"}
- `exempt_ips: List[str] = []` - IP addresses exempt from rate limiting
- `headers: bool = True` - Whether to include rate limit headers in responses

***REMOVED******REMOVED******REMOVED*** RequestConfig

- `enabled: bool = True` - Enable/disable request processing middleware
- `max_request_size: int = 10 * 1024 * 1024` - Maximum request size in bytes (10MB)
- `timeout: int = 30` - Request timeout in seconds
- `include_request_id: bool = True` - Whether to add request ID header
- `request_id_header: str = "X-Request-ID"` - Header name for request ID
- `include_process_time: bool = True` - Whether to add process time header
- `process_time_header: str = "X-Process-Time"` - Header name for process time
- `gzip_compression: bool = True` - Whether to enable gzip compression
- `gzip_minimum_size: int = 1000` - Minimum response size for compression

***REMOVED******REMOVED******REMOVED*** MetricsConfig

- `enabled: bool = True` - Enable/disable metrics collection middleware
- `endpoint_path: str = "/metrics"` - Path for the Prometheus metrics endpoint
- `include_endpoint: bool = True` - Whether to automatically add the metrics endpoint
- `exclude_paths: List[str] = ["/metrics", "/health", "/docs", "/openapi.json"]` - Paths to exclude from metrics
- `exclude_methods: List[str] = ["OPTIONS"]` - HTTP methods to exclude from metrics
- `custom_buckets: Optional[List[float]] = None` - Custom histogram buckets for request duration
- `track_request_size: bool = True` - Whether to track HTTP request sizes
- `track_response_size: bool = True` - Whether to track HTTP response sizes

***REMOVED******REMOVED*** Best Practices

***REMOVED******REMOVED******REMOVED*** 1. Environment-Specific Configurations

Create different middleware configurations for different environments:

```python
def get_middleware_config(environment: str) -> MiddlewareConfig:
    middleware = MiddlewareConfig()

    if environment == "development":
        return middleware.cors(origins=["*"]).logging(level="DEBUG")
    elif environment == "staging":
        return middleware.cors(origins=["https://staging.example.com"]).logging(level="INFO")
    elif environment == "production":
        return middleware.cors(origins=["https://app.example.com"]).security_headers().rate_limiting()

    return middleware
```

***REMOVED******REMOVED******REMOVED*** 2. Security Considerations

- Never use `origins=["*"]` with `credentials=True` in production
- Always enable security headers in production
- Use rate limiting to prevent abuse
- Be careful with request/response body logging in production
- Use trusted hosts to prevent host header attacks

***REMOVED******REMOVED******REMOVED*** 3. Performance Considerations

- Rate limiting with Redis for distributed systems
- Adjust gzip compression settings based on your content
- Monitor middleware performance impact
- Use appropriate log levels to avoid performance overhead

***REMOVED******REMOVED******REMOVED*** 4. Monitoring and Observability

- Use request IDs for tracing requests across services
- Monitor rate limit metrics
- Log security header violations
- Track middleware performance metrics
- Set up Prometheus metrics collection for production monitoring
- Configure appropriate histogram buckets for your service's latency patterns
- Monitor business metrics alongside infrastructure metrics

***REMOVED******REMOVED******REMOVED******REMOVED*** Production Metrics Setup

For production deployments, configure comprehensive metrics:

```python
***REMOVED*** Production metrics configuration
middleware.metrics(
    custom_buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
    exclude_paths=["/health", "/metrics", "/docs", "/openapi.json", "/favicon.ico"],
    track_request_size=True,
    track_response_size=True
)

***REMOVED*** Create custom business metrics
from fast_core.monitoring.metrics import get_metrics_registry

metrics = get_metrics_registry()

***REMOVED*** Service-specific metrics
api_errors = metrics.create_counter(
    "api_errors_total",
    "Total API errors",
    ["error_type", "endpoint", "service"]
)

cache_operations = metrics.create_counter(
    "cache_operations_total",
    "Cache operations",
    ["operation", "result", "cache_type"]
)

external_service_calls = metrics.create_histogram(
    "external_service_duration_seconds",
    "External service call duration",
    ["service_name", "operation", "status"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)
```

***REMOVED******REMOVED*** Testing

The middleware system includes comprehensive tests:

```bash
***REMOVED*** Run middleware tests
pytest libs/fast-core/tests/test_middleware_config.py

***REMOVED*** Run with coverage
pytest --cov=fast_core.middleware libs/fast-core/tests/test_middleware_config.py
```

***REMOVED******REMOVED*** Implementation Notes

***REMOVED******REMOVED******REMOVED*** Middleware Order

Middleware is applied in reverse order (last added = first executed):

1. Request processing (innermost)
2. **Metrics collection** - Tracks all requests including those blocked by other middleware
3. Rate limiting
4. Logging
5. Security headers
6. CORS (outermost)

This order ensures proper request flow, security header application, and comprehensive metrics collection.

***REMOVED******REMOVED******REMOVED*** Rate Limiting Implementation

The current rate limiting implementation is basic and uses in-memory storage. For production use with multiple instances, configure Redis storage:

```python
middleware.rate_limiting(storage_url="redis://localhost:6379/0")
```

***REMOVED******REMOVED******REMOVED*** Future Enhancements

- Distributed rate limiting with Redis
- Advanced CSP configuration
- Custom middleware plugins
- ✅ **Metrics and monitoring** - **IMPLEMENTED** with comprehensive Prometheus integration
- Response body logging for streaming responses
- OpenTelemetry distributed tracing integration
- Custom metrics dashboard generation
- Automated SLA monitoring and alerting

***REMOVED******REMOVED******REMOVED*** NextWatch Production Integration

The Fast Core middleware system is successfully deployed across all NextWatch services:

***REMOVED******REMOVED******REMOVED******REMOVED*** **Services with Full Middleware Stack** ✅

- **BFF API** (`bff-api:8001`) - API gateway with complete middleware stack
- **Backend API** (`backend-api:8002`) - Core data service with database metrics
- **Search API** (`search-api:8003`) - Search service with Redis performance metrics
- **Recommendation API** (`recommendation-api:8004`) - ML service with vector operation metrics
- **Auth API** (`auth-api:8005`) - Authentication service with security metrics

***REMOVED******REMOVED******REMOVED******REMOVED*** **Production Metrics**

Each service exposes comprehensive metrics at `/metrics` endpoint:

```prometheus
***REMOVED*** Example metrics from production services
http_requests_total{method="GET",endpoint="/api/v1/movies",status="200",service="bff-api"} 1543
http_request_duration_seconds{method="GET",endpoint="/api/v1/movies",le="0.1",service="bff-api"} 1325
cache_operations_total{operation="get",result="hit",cache_type="redis",service="bff-api"} 892
external_service_duration_seconds{service_name="backend-api",operation="get_movies",status="success",service="bff-api"} 0.045
```

***REMOVED******REMOVED******REMOVED******REMOVED*** **Monitoring Stack**

- **Prometheus**: Scrapes all service metrics every 15 seconds
- **Grafana**: Production dashboards for service performance, infrastructure health, and business intelligence
- **Alerting**: Real-time alerts for error rates, latency spikes, and service availability
