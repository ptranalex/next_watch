kkkkkkkk# Fast Core Tracing Migration Guide

This guide shows how to migrate from manual request ID propagation to the new automatic tracing system in Fast Core.

## Overview

The new tracing system provides:

- ✅ **Automatic request ID propagation** across services
- ✅ **OpenTelemetry integration** with W3C Trace Context
- ✅ **Zero manual implementation** required
- ✅ **Industry standard compliance** (W3C, B3, Jaeger)
- ✅ **Backward compatibility** with existing code

## Before: Manual Implementation (Error-Prone)

### Old BFF Service Code

```python
# ❌ Manual context handling (error-prone)
from bff_api.dependencies import get_backend_client, setup_request_context
from bff_api.services.clients.base import set_request_id_context

@router.get("/movies/{movie_id}")
async def get_movie_screen(
    movie_id: int,
    backend: BackendClient = Depends(get_backend_client),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    _: None = Depends(setup_request_context),  # Manual setup
):
    # Manual user ID extraction
    user_id = None
    if credentials and credentials.credentials:
        user_id = extract_user_id_from_token(credentials.credentials)

    # Manual request ID handling
    screen_data = await _get_movie_screen_data(
        movie_id, user_id, backend, recommendation_client, credentials
    )

    return screen_data

# ❌ Manual header injection in service clients
class BaseBackendClient:
    def _get_auth_headers(self, user_id: int, request_id: Optional[str] = None):
        headers = {"X-User-ID": str(user_id), "X-Service": "bff-api"}

        # Manual request ID extraction and injection
        final_request_id = request_id or get_request_id_context()
        if final_request_id:
            headers["X-Request-ID"] = final_request_id

        return headers

    async def _make_request(self, method: str, path: str, **kwargs):
        # Manual header injection
        headers = kwargs.get("headers", {})
        final_request_id = request_id or get_request_id_context()
        if final_request_id:
            headers["X-Request-ID"] = final_request_id

        # Rest of implementation...
```

### Problems with Manual Approach

1. **Human Error-Prone**: Developers forget to call `setup_request_context`
2. **Inconsistent Implementation**: Different services handle tracing differently
3. **Manual Header Injection**: Easy to miss headers in service calls
4. **Context Variable Management**: Complex manual context passing
5. **No Standard Compliance**: Custom implementation doesn't follow W3C standards

## After: Automatic Implementation (Zero Errors)

### New Fast Core Implementation

```python
# ✅ Automatic tracing with Fast Core
from fast_core import (
    create_app,
    get_current_request_context,
    get_current_request_id,
    TracingAwareServiceClient,
)
from fast_core.middleware import MiddlewareConfig

# 1. Configure middleware once
middleware = MiddlewareConfig()
middleware.context(
    service_name="bff-api",
    auto_generate_request_id=True,
    extract_user_id=True,
    trace_propagation=True,
)

# 2. Create app with automatic tracing
app = create_app(
    settings=settings,
    middleware=middleware,
    # ... other options
)

# 3. Use tracing-aware service clients
class BackendClient(TracingAwareServiceClient):
    """Backend client with automatic tracing."""

    async def get_movie(self, movie_id: int) -> Dict[str, Any]:
        # ✅ Automatic trace header injection
        # ✅ Automatic span creation
        # ✅ Automatic error handling with tracing
        response = await self.get(f"/movies/{movie_id}")
        response.raise_for_status()
        return response.json()

# 4. Clean endpoint implementation
@router.get("/movies/{movie_id}")
async def get_movie_screen(
    movie_id: int,
    request_id: str = Depends(get_current_request_id),  # ✅ Automatic
    context = Depends(get_current_request_context),     # ✅ Full context
    backend: BackendClient = Depends(get_backend_client),
):
    # ✅ All tracing happens automatically
    movie_data = await backend.get_movie(movie_id)

    return {
        "request_id": request_id,  # ✅ Always available
        "movie": movie_data,
        "trace_id": context.trace_id,  # ✅ OpenTelemetry integration
    }
```

## Migration Steps

### Step 1: Update Fast Core Configuration

```python
# In your app configuration
from fast_core.middleware import MiddlewareConfig

middleware = MiddlewareConfig()
middleware.context(
    service_name="your-service-name",
    auto_generate_request_id=True,
    extract_user_id=True,
    trace_propagation=True,
)

app = create_app(
    settings=settings,
    middleware=middleware,
    # ... existing options
)
```

### Step 2: Migrate Service Clients

```python
# Before: Manual implementation
class BackendClient(BaseServiceClient):
    def _get_auth_headers(self, user_id: int, request_id: Optional[str] = None):
        # Manual header building...
        pass

    async def _make_request(self, method: str, path: str, **kwargs):
        # Manual header injection...
        pass

# After: Automatic implementation
from fast_core.clients import TracingAwareServiceClient

class BackendClient(TracingAwareServiceClient):
    """All tracing happens automatically."""

    async def get_movie(self, movie_id: int) -> Dict[str, Any]:
        # ✅ Automatic trace headers, spans, error handling
        response = await self.get(f"/movies/{movie_id}")
        response.raise_for_status()
        return response.json()
```

### Step 3: Update Route Dependencies

```python
# Before: Manual setup
@router.get("/movies/{movie_id}")
async def get_movie(
    movie_id: int,
    backend: BackendClient = Depends(get_backend_client),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    _: None = Depends(setup_request_context),  # ❌ Manual
):
    # Manual user ID extraction
    user_id = extract_user_id_from_token(credentials.credentials) if credentials else None
    # ... rest of implementation

# After: Automatic dependencies
from fast_core import get_current_request_context, get_current_request_id

@router.get("/movies/{movie_id}")
async def get_movie(
    movie_id: int,
    request_id: str = Depends(get_current_request_id),        # ✅ Automatic
    context = Depends(get_current_request_context),           # ✅ Full context
    backend: BackendClient = Depends(get_backend_client),
):
    # ✅ Everything is automatically available
    user_id = context.user_id  # Automatic extraction
    # ... implementation
```

### Step 4: Remove Manual Context Code

```python
# ❌ Remove these manual implementations:

# Delete manual context variables
# _request_id_context: contextvars.ContextVar[Optional[str]] = ...

# Delete manual setup functions
# def set_request_id_context(request_id: Optional[str]) -> None: ...
# def get_request_id_context() -> Optional[str]: ...

# Delete manual middleware
# class RequestIDTracingMiddleware(BaseHTTPMiddleware): ...

# Delete manual header injection
# def _build_api_path(self, path: str) -> str: ...
# def _get_auth_headers(self, user_id: int, request_id: Optional[str] = None): ...
```

## Benefits After Migration

### 🚀 **Zero Manual Implementation**

- No more `setup_request_context` calls
- No more manual header injection
- No more context variable management

### 📊 **Industry Standard Compliance**

- W3C Trace Context (primary)
- B3 headers (Zipkin compatibility)
- Jaeger headers (Jaeger compatibility)
- OpenTelemetry automatic instrumentation

### 🔍 **Better Observability**

- Automatic span creation for all HTTP calls
- Proper parent-child span relationships
- Request correlation across entire service mesh
- Integration with Tempo, Jaeger, and other backends

### 🛡️ **Error Reduction**

- No human errors in trace propagation
- Consistent implementation across all services
- Automatic error handling with trace context

### ⚡ **Performance Optimized**

- Efficient context variable usage
- Minimal overhead with proper middleware ordering
- Built-in caching and connection pooling

## Backward Compatibility

The new system is **100% backward compatible**:

- ✅ Existing manual implementations continue to work
- ✅ Gradual migration possible (service by service)
- ✅ No breaking changes to existing APIs
- ✅ Existing dependencies still function

## Testing the Migration

```python
# Test automatic trace propagation
@app.get("/test-tracing")
async def test_tracing(
    context = Depends(get_current_request_context),
    backend: BackendClient = Depends(get_backend_client),
):
    """Test endpoint to verify automatic tracing."""

    # Verify context is available
    assert context is not None
    assert context.request_id is not None

    # Test automatic propagation
    response = await backend.get("/health")

    return {
        "status": "tracing_working",
        "request_id": context.request_id,
        "trace_id": context.trace_id,
        "propagation_headers": context.get_propagation_headers(),
        "backend_status": response.status_code,
    }
```

## Monitoring and Debugging

```python
# Access full trace information for debugging
@app.get("/debug/trace")
async def debug_trace(context = Depends(get_current_request_context)):
    """Debug endpoint to inspect trace context."""

    if not context:
        return {"error": "No trace context available"}

    return {
        "trace_context": context.to_dict(),
        "propagation_headers": context.get_propagation_headers(),
        "opentelemetry_trace_id": context.trace_id,
        "opentelemetry_span_id": context.span_id,
    }
```

## Next Steps

1. **Start with one service** - Migrate BFF API first
2. **Test thoroughly** - Use the debug endpoints to verify tracing
3. **Monitor logs** - Check that trace IDs appear in structured logs
4. **Migrate gradually** - Move other services one by one
5. **Remove manual code** - Clean up old implementations after migration

The new automatic tracing system eliminates human errors and provides industry-standard distributed tracing with zero manual implementation required.
