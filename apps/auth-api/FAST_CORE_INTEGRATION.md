***REMOVED*** Auth API Fast-Core Integration

This document describes the Fast-Core integration for the Auth API, providing standardized FastAPI patterns and enhanced middleware configuration.

***REMOVED******REMOVED*** Overview

The Auth API has been integrated with fast-core to provide:

- **🔒 Security-First Architecture**: Enhanced security headers and authentication-specific middleware
- **⚡ Performance Optimization**: Efficient middleware chain with auth-specific rate limiting
- **🔧 Standardized Configuration**: Consistent FastAPI patterns across all services
- **📊 Enhanced Monitoring**: Request tracing and authentication flow monitoring
- **🛡️ Security Hardening**: Production-ready security configurations

***REMOVED******REMOVED*** Architecture

***REMOVED******REMOVED******REMOVED*** Fast-Core App Factory

The auth service uses a dedicated app factory (`create_auth_app`) that:

```python
from auth_api.core.app_fast_core import create_auth_app
from auth_api.config.app import Config

config = Config()
app = create_auth_app(config)
```

***REMOVED******REMOVED******REMOVED*** Key Features

***REMOVED******REMOVED******REMOVED******REMOVED*** 1. **Auth-Specific Middleware Stack**

```python
def create_auth_middleware_config(config: Config) -> MiddlewareConfig:
    middleware = MiddlewareConfig()

    ***REMOVED*** CORS - Restrictive for auth service
    middleware.cors(
        origins=config.cors_origins,
        credentials=True,  ***REMOVED*** Required for auth cookies/tokens
        methods=["POST", "GET", "OPTIONS"],  ***REMOVED*** Limited to auth operations
        headers=["Content-Type", "Authorization", "X-Request-ID"],
        max_age=300,  ***REMOVED*** Short cache for auth endpoints (5 minutes)
    )

    ***REMOVED*** Enhanced Security Headers
    if is_production:
        middleware.security_headers(
            hsts=True,
            frame_options="DENY",  ***REMOVED*** Prevent iframe attacks
            csp="default-src 'self'",
            trusted_hosts=config.allowed_hosts,
        )

    ***REMOVED*** Auth-Specific Rate Limiting
    rate_limit_config = {
        "/auth/login": "10/minute",           ***REMOVED*** Login attempts
        "/auth/register": "5/minute",         ***REMOVED*** Registration attempts
        "/auth/refresh": "30/minute",         ***REMOVED*** Token refresh
        "/auth/password/reset": "3/minute",   ***REMOVED*** Password reset
        "/auth/verify": "100/minute",         ***REMOVED*** Token verification
    }

    middleware.rate_limiting(
        default_limit="100/minute",
        endpoints=rate_limit_config,
        key_func="ip",
    )
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 2. **Security Hardening**

- **Restrictive CORS**: Limited to essential auth operations only
- **Enhanced Headers**: HSTS, CSP, Frame Options for iframe protection
- **Rate Limiting**: Aggressive limits on sensitive endpoints (login, registration)
- **Request Validation**: Size limits and timeout configuration

***REMOVED******REMOVED******REMOVED******REMOVED*** 3. **Authentication Flow Monitoring**

- **Request Tracing**: Correlation IDs for tracking auth requests
- **Performance Metrics**: Process time headers for monitoring
- **Structured Logging**: Auth-specific log patterns with sensitive data filtering

***REMOVED******REMOVED*** Implementation Details

***REMOVED******REMOVED******REMOVED*** 1. **Configuration Adapter**

**File**: `src/auth_api/config/fast_core_config.py`

While the full FastAPIConfig integration is being refined, the current implementation uses direct FastAPI configuration with fast-core middleware patterns.

***REMOVED******REMOVED******REMOVED*** 2. **App Factory**

**File**: `src/auth_api/core/app_fast_core.py`

```python
def create_auth_app(config: Optional[Config] = None) -> FastAPI:
    """Create Auth API application using fast-core with enhanced middleware."""

    ***REMOVED*** Create Auth-specific middleware configuration
    middleware_config = create_auth_middleware_config(config)

    ***REMOVED*** Create FastAPI app with auth-specific settings
    app = FastAPI(
        title="Next Watch Authentication API",
        description="Dedicated authentication service for Next Watch movie platform",
        version="0.1.0",
        debug=config.debug,
        lifespan=auth_lifespan,
        docs_url="/docs" if config.debug else None,
        redoc_url="/redoc" if config.debug else None,
        openapi_url="/openapi.json" if config.debug else None,
    )

    ***REMOVED*** Apply middleware and include routers
    setup_middleware(app)
    include_auth_routers(app)

    return app
```

***REMOVED******REMOVED******REMOVED*** 3. **Lifecycle Management**

```python
@asynccontextmanager
async def auth_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Auth API lifespan manager with database and health service initialization."""
    ***REMOVED*** Startup
    init_database()
    app.state.health_service = get_health_service()

    yield

    ***REMOVED*** Shutdown
    close_health_service()
```

***REMOVED******REMOVED*** Security Configuration

***REMOVED******REMOVED******REMOVED*** Production Security Settings

- **HSTS**: 1 year max-age with subdomain inclusion
- **CSP**: Strict `default-src 'self'` policy
- **Frame Options**: `DENY` to prevent iframe attacks
- **Trusted Hosts**: Configured from `allowed_hosts` setting
- **Rate Limiting**: Aggressive limits on auth endpoints

***REMOVED******REMOVED******REMOVED*** Development Security Settings

- **HSTS**: Disabled for local development
- **CSP**: Permissive policy for development tools
- **Frame Options**: `SAMEORIGIN` for debugging
- **Rate Limiting**: Higher limits for testing

***REMOVED******REMOVED*** Route Organization

***REMOVED******REMOVED******REMOVED*** Core Auth Routes

- **`/auth/login`**: User authentication endpoint
- **`/auth/register`**: User registration endpoint
- **`/auth/refresh`**: Token refresh endpoint
- **`/auth/logout`**: User logout endpoint
- **`/auth/verify`**: Token verification endpoint
- **`/auth/password/reset`**: Password reset flow

***REMOVED******REMOVED******REMOVED*** Health and Meta Routes

- **`/health`**: Service health checks
- **`/meta`**: Service metadata and information

***REMOVED******REMOVED*** Integration Benefits

***REMOVED******REMOVED******REMOVED*** 1. **Consistency with Other Services**

- Standardized middleware patterns matching `backend-api` and `bff-api`
- Common logging and monitoring approaches
- Unified security header configuration

***REMOVED******REMOVED******REMOVED*** 2. **Auth-Specific Optimizations**

- **Restrictive CORS**: Only allows necessary auth operations
- **Aggressive Rate Limiting**: Protects against brute force attacks
- **Security Headers**: Enhanced protection for authentication flows
- **Request Validation**: Strict limits on auth request sizes

***REMOVED******REMOVED******REMOVED*** 3. **Production Readiness**

- **Security Hardening**: Production-grade security configurations
- **Performance Monitoring**: Request tracing and timing metrics
- **Error Handling**: Structured error responses and logging
- **Health Checks**: Service health monitoring and database connectivity

***REMOVED******REMOVED*** Usage Examples

***REMOVED******REMOVED******REMOVED*** Basic App Creation

```python
from auth_api.core.app_fast_core import create_auth_app

***REMOVED*** Create app with default configuration
app = create_auth_app()
```

***REMOVED******REMOVED******REMOVED*** Custom Configuration

```python
from auth_api.core.app_fast_core import create_auth_app
from auth_api.config.app import Config

***REMOVED*** Create custom configuration
config = Config(
    api_port=8003,
    debug=False,
    cors_origins=["https://app.nextwatch.com"],
    jwt_secret="production-secret-key"
)

***REMOVED*** Create app with custom config
app = create_auth_app(config)
```

***REMOVED******REMOVED******REMOVED*** Development vs Production

```python
***REMOVED*** Development
config = Config(debug=True, log_level="DEBUG")
app = create_auth_app(config)  ***REMOVED*** Permissive security, verbose logging

***REMOVED*** Production
config = Config(debug=False, log_level="INFO")
app = create_auth_app(config)  ***REMOVED*** Strict security, optimized logging
```

***REMOVED******REMOVED*** Migration Notes

***REMOVED******REMOVED******REMOVED*** From Legacy App Factory

The new fast-core app factory provides enhanced features while maintaining compatibility:

```python
***REMOVED*** Legacy
from auth_api.core.app import create_app
app = create_app()

***REMOVED*** Fast-Core Enhanced
from auth_api.core.app_fast_core import create_auth_app
app = create_auth_app()  ***REMOVED*** Enhanced middleware, better security
```

***REMOVED******REMOVED******REMOVED*** Configuration Compatibility

The existing `auth_api.config.app.Config` class works directly with the new app factory without changes.

***REMOVED******REMOVED*** Future Enhancements

***REMOVED******REMOVED******REMOVED*** Planned Features

1. **Full FastAPIConfig Integration**: Complete config adapter once parsing issues are resolved
2. **JWT Middleware Integration**: Direct JWT validation in middleware chain
3. **Advanced Rate Limiting**: Redis-backed distributed rate limiting
4. **Metrics Integration**: Prometheus metrics for auth flows
5. **Distributed Tracing**: OpenTelemetry integration for auth requests

***REMOVED******REMOVED******REMOVED*** Performance Improvements

1. **Connection Pooling**: Optimized database connection management
2. **Caching Layer**: Redis integration for session and token caching
3. **Async Optimization**: Full async/await patterns throughout auth flows

***REMOVED******REMOVED*** Testing

***REMOVED******REMOVED******REMOVED*** Integration Tests

```python
from auth_api.core.app_fast_core import create_auth_app
from fastapi.testclient import TestClient

def test_auth_app_creation():
    app = create_auth_app()
    client = TestClient(app)

    ***REMOVED*** Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200

    ***REMOVED*** Test middleware headers
    assert "X-Request-ID" in response.headers
```

***REMOVED******REMOVED******REMOVED*** Security Tests

```python
def test_security_headers():
    app = create_auth_app()
    client = TestClient(app)

    response = client.get("/health")

    ***REMOVED*** Check security headers
    assert "X-Frame-Options" in response.headers
    assert "X-Content-Type-Options" in response.headers
```

***REMOVED******REMOVED*** Conclusion

The Auth API fast-core integration provides a robust, secure, and performant foundation for authentication services. The implementation follows established patterns while adding auth-specific optimizations for security and performance.

The integration enhances the authentication service with:

- ✅ **Enhanced Security**: Production-grade security headers and rate limiting
- ✅ **Standardized Patterns**: Consistent middleware configuration across services
- ✅ **Performance Monitoring**: Request tracing and performance metrics
- ✅ **Production Readiness**: Environment-specific configuration and optimization
- ✅ **Developer Experience**: Comprehensive documentation and testing patterns

This integration positions the Auth API as a secure, scalable, and maintainable component of the Next Watch platform.
