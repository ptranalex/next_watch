***REMOVED*** Enhanced Error Handling Migration Guide

***REMOVED******REMOVED*** Overview

This guide provides step-by-step instructions for migrating services to use the enhanced error handling system in `fast-core`. The system provides semantic error preservation, graceful degradation, and improved observability while maintaining backward compatibility.

***REMOVED******REMOVED*** 🎯 Benefits of Migration

- **Semantic Preservation**: 404s stay 404s, 401s stay 401s (instead of generic 502s)
- **Graceful Degradation**: Optional services can fail without breaking core functionality
- **Enhanced Logging**: Rich context and semantic information for debugging
- **Better Monitoring**: Proper HTTP status codes and error categorization
- **User Experience**: More specific, actionable error messages

***REMOVED******REMOVED*** 🔄 Migration Patterns

***REMOVED******REMOVED******REMOVED*** Pattern 1: Simple Service Decorator Replacement

**Before:**

```python
@service_error_handler("external-api", logger)
async def get_data():
    return await external_api.fetch()
```

**After:**

```python
@critical_service_handler("external-api", logger)
async def get_data():
    return await external_api.fetch()
```

***REMOVED******REMOVED******REMOVED*** Pattern 2: Optional Service with Graceful Degradation

**Before:**

```python
@service_error_handler("recommendation-api", logger)
async def get_recommendations():
    try:
        return await reco_api.get_similar()
    except Exception:
        return []  ***REMOVED*** Manual fallback
```

**After:**

```python
@optional_service_handler(
    service_name="recommendation-api",
    logger=logger,
    fallback_value=[]
)
async def get_recommendations():
    return await reco_api.get_similar()  ***REMOVED*** Automatic fallback
```

***REMOVED******REMOVED******REMOVED*** Pattern 3: Custom Error Mapping

**Before:**

```python
@service_error_handler("auth-api", logger)
async def login(credentials):
    try:
        return await auth_api.login(credentials)
    except Exception as e:
        if "invalid credentials" in str(e):
            raise HTTPException(401, "Invalid credentials")
        raise HTTPException(500, "Login failed")
```

**After:**

```python
@service_error_handler(
    service_name="auth-api",
    logger=logger,
    preserve_semantics=True,
    error_mapping={
        "invalid_credentials": lambda e: AuthenticationException("Invalid credentials"),
        "account_locked": lambda e: AuthenticationException("Account locked"),
    }
)
async def login(credentials):
    return await auth_api.login(credentials)
```

***REMOVED******REMOVED*** 📋 Step-by-Step Migration Process

***REMOVED******REMOVED******REMOVED*** Step 1: Assessment

1. **Identify Service Calls**: Find all functions using `@service_error_handler`
2. **Classify Operations**: Determine if each operation is critical or optional
3. **Review Error Handling**: Identify manual error handling that can be automated
4. **Business Logic Errors**: Identify domain-specific errors that need custom mapping

```bash
***REMOVED*** Find all service error handlers
grep -r "@service_error_handler" src/
grep -r "service_error_handler(" src/
```

***REMOVED******REMOVED******REMOVED*** Step 2: Choose the Right Decorator

***REMOVED******REMOVED******REMOVED******REMOVED*** Critical Service Handler

Use for operations that must succeed for the application to function:

```python
@critical_service_handler("database", logger)
async def get_user(user_id: int):
    ***REMOVED*** User data is essential - if this fails, return 502
    return await db.get_user(user_id)
```

**When to use:**

- Database operations
- Core business logic
- Authentication/authorization
- Essential data retrieval

***REMOVED******REMOVED******REMOVED******REMOVED*** Optional Service Handler

Use for operations that enhance the experience but aren't essential:

```python
@optional_service_handler(
    service_name="recommendations",
    logger=logger,
    fallback_value=[]
)
async def get_similar_movies():
    ***REMOVED*** Recommendations are nice-to-have - gracefully degrade if unavailable
    return await reco_service.get_similar()
```

**When to use:**

- Recommendations
- Analytics/tracking
- Non-essential enrichment data
- Third-party integrations

***REMOVED******REMOVED******REMOVED******REMOVED*** Custom Error Mapping

Use when you need to preserve specific business logic errors:

```python
@service_error_handler(
    service_name="payment-api",
    logger=logger,
    preserve_semantics=True,
    error_mapping={
        "insufficient_funds": lambda e: PaymentException("Insufficient funds"),
        "card_expired": lambda e: PaymentException("Card expired"),
    }
)
async def process_payment():
    return await payment_api.charge(amount)
```

**When to use:**

- Authentication flows
- Payment processing
- Business rule violations
- Domain-specific errors

***REMOVED******REMOVED******REMOVED*** Step 3: Update Imports

Add the new error handling imports:

```python
from fast_core.errors import (
    critical_service_handler,
    optional_service_handler,
    service_error_handler,  ***REMOVED*** Keep for custom mapping
    ValidationException,
    AuthenticationException,
    ConflictException,
    ***REMOVED*** Add other exceptions as needed
)
```

***REMOVED******REMOVED******REMOVED*** Step 4: Replace Decorators

***REMOVED******REMOVED******REMOVED******REMOVED*** For Critical Operations:

```python
***REMOVED*** Before
@service_error_handler("database", logger)

***REMOVED*** After
@critical_service_handler("database", logger)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** For Optional Operations:

```python
***REMOVED*** Before
@service_error_handler("optional-service", logger)
async def get_optional_data():
    try:
        return await service.get_data()
    except Exception:
        return []

***REMOVED*** After
@optional_service_handler(
    service_name="optional-service",
    logger=logger,
    fallback_value=[]
)
async def get_optional_data():
    return await service.get_data()
```

***REMOVED******REMOVED******REMOVED*** Step 5: Handle Custom Client Errors

For clients that raise custom exceptions (like `BackendClientPermanentError`), convert them to semantic exceptions:

```python
class RecommendationClient(BaseBackendClient):
    async def _make_request(self, method, path, params=None, data=None, headers=None):
        try:
            return await super()._make_request(method, path, params, data, headers)
        except BackendClientPermanentError as e:
            if "404" in str(e):
                raise ResourceNotFoundException(
                    detail="Resource not found in recommendation service",
                    resource_type="Movie",
                    resource_id="unknown"
                )
            raise

    @optional_service_handler(
        service_name="recommendation-api",
        logger=logger,
        fallback_value=[]
    )
    async def get_similar_movies(self, movie_id: int):
        return await self._make_request("GET", f"/movies/{movie_id}/similar")
```

***REMOVED******REMOVED******REMOVED*** Step 6: Remove Manual Error Handling

Remove manual `try/except` blocks that are now handled automatically:

```python
***REMOVED*** Before
@service_error_handler("external-api", logger)
async def get_data():
    try:
        data = await external_api.fetch()
        return data
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        return []

***REMOVED*** After
@optional_service_handler(
    service_name="external-api",
    logger=logger,
    fallback_value=[]
)
async def get_data():
    return await external_api.fetch()
```

***REMOVED******REMOVED******REMOVED*** Step 7: Update Tests

Update tests to expect the new exception types:

```python
***REMOVED*** Before
with pytest.raises(HTTPException) as exc_info:
    await service.get_data()
assert exc_info.value.status_code == 502

***REMOVED*** After
with pytest.raises(ResourceNotFoundException):
    await service.get_data()
```

***REMOVED******REMOVED*** 🔍 Service-Specific Patterns

***REMOVED******REMOVED******REMOVED*** BFF API Clients

**Pattern**: Classify operations by criticality and add appropriate fallbacks

```python
***REMOVED*** Critical: Core movie data
@critical_service_handler("backend-api", logger)
async def get_movie(self, movie_id: int):
    return await self._make_request("GET", f"/movies/{movie_id}")

***REMOVED*** Optional: Enhancement data
@optional_service_handler(
    service_name="backend-api",
    logger=logger,
    fallback_value=[]
)
async def get_movie_trailers(self, movie_id: int):
    return await self._make_request("GET", f"/movies/{movie_id}/trailers")
```

***REMOVED******REMOVED******REMOVED*** Auth API

**Pattern**: Preserve authentication semantics and add input validation

```python
@service_error_handler(
    service_name="auth-database",
    logger=logger,
    preserve_semantics=True,
    error_mapping={
        "invalid_credentials": lambda e: AuthenticationException("Invalid credentials"),
        "account_locked": lambda e: AuthenticationException("Account locked"),
    }
)
async def authenticate_user(email: str, password: str):
    ***REMOVED*** Validate input
    if not email or not password:
        raise ValidationException("Email and password required")

    return await auth_service.authenticate(email, password)
```

***REMOVED******REMOVED******REMOVED*** Search API

**Pattern**: Redis operations with graceful degradation

```python
@optional_service_handler(
    service_name="redis",
    logger=logger,
    fallback_value=[]
)
async def get_suggestions(self, query: str):
    return await redis_client.get_suggestions(query)
```

***REMOVED******REMOVED******REMOVED*** Database Operations

**Pattern**: Critical operations with semantic error preservation

```python
@critical_service_handler("auth-database", logger)
def create_user(session: Session, email: str, password: str):
    ***REMOVED*** Check for conflicts
    existing = get_user_by_email(session, email)
    if existing:
        raise ValueError("email already exists")  ***REMOVED*** Will be mapped to ConflictException

    ***REMOVED*** Create user...
    return user
```

***REMOVED******REMOVED*** ⚠️ Common Pitfalls

***REMOVED******REMOVED******REMOVED*** 1. Wrong Decorator Choice

**❌ Wrong:**

```python
@optional_service_handler(...)  ***REMOVED*** Wrong for essential operations
async def get_user_profile():
    return await db.get_user()  ***REMOVED*** User profile is critical!
```

**✅ Correct:**

```python
@critical_service_handler("database", logger)
async def get_user_profile():
    return await db.get_user()
```

***REMOVED******REMOVED******REMOVED*** 2. Missing Fallback Values

**❌ Wrong:**

```python
@optional_service_handler("external-api", logger)  ***REMOVED*** Missing fallback_value
async def get_optional_data():
    return await api.get_data()  ***REMOVED*** Will return None on failure
```

**✅ Correct:**

```python
@optional_service_handler(
    service_name="external-api",
    logger=logger,
    fallback_value=[]  ***REMOVED*** Appropriate fallback
)
async def get_optional_data():
    return await api.get_data()
```

***REMOVED******REMOVED******REMOVED*** 3. Over-Complex Error Mapping

**❌ Wrong:**

```python
error_mapping={
    "any_error": lambda e: CustomException(str(e)),  ***REMOVED*** Too broad
    "another_error": lambda e: AnotherException(str(e)),  ***REMOVED*** Too many mappings
}
```

**✅ Correct:**

```python
error_mapping={
    "invalid_credentials": lambda e: AuthenticationException("Invalid credentials"),
    ***REMOVED*** Only map specific, actionable errors
}
```

***REMOVED******REMOVED******REMOVED*** 4. Circular Imports

**❌ Wrong:**

```python
***REMOVED*** In app_factory.py
from routes.api_v1 import router  ***REMOVED*** At module level

***REMOVED*** In routes/api_v1.py
from core.app_factory import some_function  ***REMOVED*** Circular import!
```

**✅ Correct:**

```python
***REMOVED*** In app_factory.py
def create_app():
    from routes.api_v1 import router  ***REMOVED*** Import locally
    ***REMOVED*** Use router...
```

***REMOVED******REMOVED*** 🧪 Testing Patterns

***REMOVED******REMOVED******REMOVED*** Test Error Handling

```python
async def test_critical_service_failure():
    """Test that critical service failures raise appropriate exceptions."""
    with patch('service.external_call') as mock_call:
        mock_call.side_effect = ConnectionError("Database unavailable")

        with pytest.raises(ExternalServiceException) as exc_info:
            await critical_operation()

        assert "Database unavailable" in str(exc_info.value)

async def test_optional_service_graceful_degradation():
    """Test that optional service failures return fallback values."""
    with patch('service.external_call') as mock_call:
        mock_call.side_effect = ConnectionError("Service unavailable")

        result = await optional_operation()
        assert result == []  ***REMOVED*** Fallback value
```

***REMOVED******REMOVED******REMOVED*** Test Error Mapping

```python
async def test_auth_error_mapping():
    """Test that authentication errors are properly mapped."""
    with patch('auth_service.authenticate') as mock_auth:
        mock_auth.side_effect = ValueError("invalid_credentials")

        with pytest.raises(AuthenticationException) as exc_info:
            await login_user("user@example.com", "wrong_password")

        assert "Invalid credentials" in str(exc_info.value)
```

***REMOVED******REMOVED*** 📊 Monitoring and Observability

***REMOVED******REMOVED******REMOVED*** Log Analysis

The enhanced error handling provides rich context:

```python
***REMOVED*** Before: Generic error
ERROR: Service error in get_movie: 500 Internal Server Error

***REMOVED*** After: Semantic context
ERROR: [CRITICAL] backend-api unavailable in get_movie
  operation=get_movie service=backend-api
  movie_id=123 error_type=ExternalServiceException
  original_error="Connection timeout after 30s"
```

***REMOVED******REMOVED******REMOVED*** Metrics

Monitor error patterns:

```python
***REMOVED*** Custom metrics for error patterns
error_rate_by_type = Counter('errors_by_type', ['service', 'error_type', 'operation'])
graceful_degradation_count = Counter('graceful_degradations', ['service', 'operation'])
```

***REMOVED******REMOVED******REMOVED*** Alerts

Set up appropriate alerting:

```yaml
***REMOVED*** Critical service failures
- alert: CriticalServiceFailure
  expr: rate(errors_by_type{error_type="ExternalServiceException"}[5m]) > 0.1

***REMOVED*** Graceful degradation monitoring
- alert: HighGracefulDegradation
  expr: rate(graceful_degradations[15m]) > 10
```

***REMOVED******REMOVED*** 🚀 Rollout Strategy

***REMOVED******REMOVED******REMOVED*** 1. Development Environment

1. Update development services first
2. Test all error scenarios
3. Verify graceful degradation
4. Check log quality

***REMOVED******REMOVED******REMOVED*** 2. Staging Environment

1. Deploy with feature flag enabled
2. Run integration tests
3. Load test error conditions
4. Monitor error patterns

***REMOVED******REMOVED******REMOVED*** 3. Production Rollout

1. Deploy with feature flag disabled
2. Enable for small percentage of traffic
3. Monitor metrics and logs
4. Gradually increase percentage
5. Full rollout after validation

***REMOVED******REMOVED*** 📚 Additional Resources

- [Enhanced Error Handling Documentation](./ENHANCED_ERROR_HANDLING.md)
- [Fast-Core Examples](../examples/error_handling_demo.py)
- [Adoption Strategy](./ADOPTION_STRATEGY.md)
- [Error Handling Best Practices](./ERROR_HANDLING_BEST_PRACTICES.md)

***REMOVED******REMOVED*** 🆘 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Import Errors

```python
***REMOVED*** If you get "cannot import name 'critical_service_handler'"
***REMOVED*** Check that fast-core is updated:
pip install --upgrade fast-core

***REMOVED*** Verify imports:
from fast_core.errors import critical_service_handler
```

***REMOVED******REMOVED******REMOVED*** Circular Import Issues

```python
***REMOVED*** Move router imports to function level:
def create_app():
    from routes import router  ***REMOVED*** Local import
    app.include_router(router)
```

***REMOVED******REMOVED******REMOVED*** Type Errors

```python
***REMOVED*** If decorators complain about return types:
@critical_service_handler("service", logger)
async def my_function() -> MyType:  ***REMOVED*** Specify return type
    return await service.call()
```

***REMOVED******REMOVED*** 📞 Support

For questions or issues with migration:

1. Check existing examples in `libs/fast-core/examples/`
2. Review service implementations in `apps/*/src/*/services/`
3. Consult the adoption strategy for patterns
4. Create an issue with migration questions

---

This migration guide provides the foundation for adopting enhanced error handling across the Next Watch platform. Follow the patterns consistently for the best results.
