***REMOVED*** Error Handling Best Practices

***REMOVED******REMOVED*** Overview

This document outlines best practices for error handling in microservices using the enhanced error handling system. Following these patterns ensures consistent, maintainable, and observable error handling across the Next Watch platform.

***REMOVED******REMOVED*** 🎯 Core Principles

***REMOVED******REMOVED******REMOVED*** 1. Semantic Preservation

**Principle**: HTTP status codes should reflect the actual nature of the error, not the implementation details.

```python
***REMOVED*** ❌ Bad: All errors become 502
@service_error_handler("user-service", logger)
async def get_user(user_id: int):
    return await user_service.get(user_id)  ***REMOVED*** 404 becomes 502

***REMOVED*** ✅ Good: Preserve semantic meaning
@critical_service_handler("user-service", logger)
async def get_user(user_id: int):
    return await user_service.get(user_id)  ***REMOVED*** 404 stays 404
```

***REMOVED******REMOVED******REMOVED*** 2. Graceful Degradation

**Principle**: Non-critical features should fail silently without breaking core functionality.

```python
***REMOVED*** ❌ Bad: Recommendations failure breaks movie page
@critical_service_handler("recommendation-api", logger)
async def get_similar_movies():
    return await reco_api.get_similar()  ***REMOVED*** Failure = 502 error page

***REMOVED*** ✅ Good: Graceful degradation
@optional_service_handler(
    service_name="recommendation-api",
    logger=logger,
    fallback_value=[]
)
async def get_similar_movies():
    return await reco_api.get_similar()  ***REMOVED*** Failure = empty recommendations
```

***REMOVED******REMOVED******REMOVED*** 3. Context-Rich Logging

**Principle**: Error logs should provide sufficient context for debugging and monitoring.

```python
***REMOVED*** ❌ Bad: Generic error message
logger.error("Service failed")

***REMOVED*** ✅ Good: Rich context provided automatically
@critical_service_handler("database", logger)  ***REMOVED*** Includes operation, service, timing
async def get_user_data(user_id: int):
    return await db.get_user(user_id)
```

***REMOVED******REMOVED*** 📋 Decision Framework

***REMOVED******REMOVED******REMOVED*** Choosing the Right Decorator

***REMOVED******REMOVED******REMOVED******REMOVED*** Critical Service Handler

**Use when**: The operation is essential for core functionality

```python
@critical_service_handler("service-name", logger)
```

**Examples**:

- User authentication
- Core data retrieval
- Payment processing
- Database operations

**Characteristics**:

- Failure prevents the operation from completing
- Users expect an error if this fails
- Alternative flows are not acceptable

***REMOVED******REMOVED******REMOVED******REMOVED*** Optional Service Handler

**Use when**: The operation enhances the experience but isn't required

```python
@optional_service_handler(
    service_name="service-name",
    logger=logger,
    fallback_value=appropriate_default
)
```

**Examples**:

- Recommendations
- Analytics/tracking
- Social features
- Performance optimizations

**Characteristics**:

- Failure doesn't break core user flows
- Acceptable fallback values exist
- Users may not notice the absence

***REMOVED******REMOVED******REMOVED******REMOVED*** Custom Error Mapping

**Use when**: You need to preserve specific business logic semantics

```python
@service_error_handler(
    service_name="service-name",
    logger=logger,
    preserve_semantics=True,
    error_mapping={...}
)
```

**Examples**:

- Authentication flows (401, 403 errors)
- Payment validation (specific payment errors)
- Business rule violations
- Multi-step workflows

**Characteristics**:

- Domain-specific error handling required
- Multiple error types need different responses
- Business logic embedded in error handling

***REMOVED******REMOVED*** 🔧 Implementation Patterns

***REMOVED******REMOVED******REMOVED*** Pattern 1: Database Operations

```python
@critical_service_handler("database", logger)
async def get_user(session: Session, user_id: int) -> User:
    """Get user by ID - critical for authentication flows."""
    user = session.get(User, user_id)
    if not user:
        raise ResourceNotFoundException(
            detail=f"User with ID {user_id} not found",
            resource_type="User",
            resource_id=str(user_id)
        )
    return user

@critical_service_handler("database", logger)
async def create_user(session: Session, email: str) -> User:
    """Create user - critical for registration."""
    ***REMOVED*** Check for conflicts first
    existing = get_user_by_email(session, email)
    if existing:
        ***REMOVED*** Will be mapped to ConflictException by error mapping
        raise ValueError("email already exists")

    return User(email=email)
```

***REMOVED******REMOVED******REMOVED*** Pattern 2: External API Calls

```python
***REMOVED*** Critical business data
@critical_service_handler("payment-api", logger)
async def process_payment(amount: float) -> PaymentResult:
    """Process payment - must succeed for purchase."""
    return await payment_api.charge(amount)

***REMOVED*** Enhancement data
@optional_service_handler(
    service_name="analytics-api",
    logger=logger,
    fallback_value={"events": []}
)
async def track_user_event(event: dict) -> dict:
    """Track analytics - nice to have but not essential."""
    return await analytics_api.track(event)
```

***REMOVED******REMOVED******REMOVED*** Pattern 3: Authentication Flows

```python
@service_error_handler(
    service_name="auth-database",
    logger=logger,
    preserve_semantics=True,
    error_mapping={
        "invalid_credentials": lambda e: AuthenticationException("Invalid email or password"),
        "account_locked": lambda e: AuthenticationException("Account temporarily locked"),
        "account_disabled": lambda e: AuthenticationException("Account is disabled"),
    }
)
async def authenticate_user(email: str, password: str) -> User:
    """Authenticate user with semantic error preservation."""
    ***REMOVED*** Input validation
    if not email or not password:
        raise ValidationException("Email and password are required")

    ***REMOVED*** Attempt authentication
    user = await auth_service.authenticate(email, password)
    if not user:
        raise ValueError("invalid_credentials")  ***REMOVED*** Mapped to AuthenticationException

    return user
```

***REMOVED******REMOVED******REMOVED*** Pattern 4: Multi-Service Orchestration

```python
async def get_movie_details(movie_id: int) -> MovieDetails:
    """Get comprehensive movie details from multiple services."""

    ***REMOVED*** Critical: Basic movie data
    movie = await get_movie_basic_data(movie_id)  ***REMOVED*** @critical_service_handler

    ***REMOVED*** Optional: Enhancement data with fallbacks
    cast = await get_movie_cast(movie_id)  ***REMOVED*** @optional_service_handler -> []
    trailers = await get_movie_trailers(movie_id)  ***REMOVED*** @optional_service_handler -> []
    recommendations = await get_similar_movies(movie_id)  ***REMOVED*** @optional_service_handler -> []

    return MovieDetails(
        movie=movie,
        cast=cast,  ***REMOVED*** May be empty on service failure
        trailers=trailers,  ***REMOVED*** May be empty on service failure
        recommendations=recommendations  ***REMOVED*** May be empty on service failure
    )
```

***REMOVED******REMOVED*** 🚨 Anti-Patterns

***REMOVED******REMOVED******REMOVED*** 1. Wrong Criticality Classification

```python
***REMOVED*** ❌ Bad: Optional data marked as critical
@critical_service_handler("recommendation-api", logger)
async def get_movie_suggestions():
    return await reco_api.get_suggestions()  ***REMOVED*** Page breaks if recommendations fail

***REMOVED*** ✅ Good: Proper classification
@optional_service_handler(
    service_name="recommendation-api",
    logger=logger,
    fallback_value=[]
)
async def get_movie_suggestions():
    return await reco_api.get_suggestions()  ***REMOVED*** Page works without recommendations
```

***REMOVED******REMOVED******REMOVED*** 2. Missing Fallback Values

```python
***REMOVED*** ❌ Bad: No fallback specified
@optional_service_handler("external-api", logger)  ***REMOVED*** Returns None on failure
async def get_optional_data():
    return await api.get_data()

***REMOVED*** ✅ Good: Appropriate fallback
@optional_service_handler(
    service_name="external-api",
    logger=logger,
    fallback_value={"data": [], "status": "unavailable"}
)
async def get_optional_data():
    return await api.get_data()
```

***REMOVED******REMOVED******REMOVED*** 3. Over-Complex Error Mapping

```python
***REMOVED*** ❌ Bad: Too many specific mappings
@service_error_handler(
    service_name="api",
    logger=logger,
    error_mapping={
        "connection_timeout": lambda e: TimeoutException("Timeout"),
        "connection_refused": lambda e: ServiceException("Refused"),
        "dns_error": lambda e: NetworkException("DNS"),
        "ssl_error": lambda e: SecurityException("SSL"),
        ***REMOVED*** ... 20 more mappings
    }
)

***REMOVED*** ✅ Good: Focus on actionable business errors
@service_error_handler(
    service_name="payment-api",
    logger=logger,
    preserve_semantics=True,
    error_mapping={
        "insufficient_funds": lambda e: PaymentException("Insufficient funds"),
        "invalid_card": lambda e: PaymentException("Card declined"),
    }
)
```

***REMOVED******REMOVED******REMOVED*** 4. Manual Error Handling in Decorated Functions

```python
***REMOVED*** ❌ Bad: Manual error handling defeats the purpose
@optional_service_handler("api", logger, fallback_value=[])
async def get_data():
    try:
        return await api.fetch()
    except Exception as e:
        logger.error(f"Manual error handling: {e}")  ***REMOVED*** Decorator handles this
        return []  ***REMOVED*** Decorator provides fallback

***REMOVED*** ✅ Good: Let decorator handle errors
@optional_service_handler("api", logger, fallback_value=[])
async def get_data():
    return await api.fetch()  ***REMOVED*** Clean, decorator handles errors and fallbacks
```

***REMOVED******REMOVED*** 📝 Documentation Standards

***REMOVED******REMOVED******REMOVED*** Function Documentation

```python
@critical_service_handler("user-database", logger)
async def get_user_profile(user_id: int) -> UserProfile:
    """Get user profile data.

    This is a CRITICAL operation - user profile access must always work
    for the platform to function properly.

    Args:
        user_id: User identifier

    Returns:
        User profile data

    Raises:
        ValidationException: If user_id is invalid
        ResourceNotFoundException: If user not found
        ExternalServiceException: If database is unavailable (critical failure)
    """
    if user_id <= 0:
        raise ValidationException("User ID must be positive")
    return await db.get_user_profile(user_id)
```

***REMOVED******REMOVED******REMOVED*** Error Mapping Documentation

```python
@service_error_handler(
    service_name="auth-api",
    logger=logger,
    preserve_semantics=True,
    error_mapping={
        ***REMOVED*** Map auth service errors to semantic exceptions
        "invalid_credentials": lambda e: AuthenticationException("Invalid email or password"),
        "account_locked": lambda e: AuthenticationException("Account temporarily locked"),
        "token_expired": lambda e: AuthenticationException("Session expired"),
    }
)
async def validate_user_session(token: str):
    """Validate user session token.

    Error mapping preserves authentication semantics:
    - invalid_credentials -> 401 AuthenticationException
    - account_locked -> 401 AuthenticationException
    - token_expired -> 401 AuthenticationException
    - Other errors -> 502 ExternalServiceException
    """
    return await auth_service.validate_token(token)
```

***REMOVED******REMOVED*** 🧪 Testing Best Practices

***REMOVED******REMOVED******REMOVED*** Test Critical Operations

```python
async def test_critical_operation_database_failure():
    """Critical operations should raise ExternalServiceException on infrastructure failure."""
    with patch('database.get_user') as mock_db:
        mock_db.side_effect = ConnectionError("Database unavailable")

        with pytest.raises(ExternalServiceException) as exc_info:
            await get_user_profile(123)

        assert "Database unavailable" in str(exc_info.value)
        assert exc_info.value.status_code == 502

async def test_critical_operation_business_logic_error():
    """Critical operations should preserve business logic errors."""
    with patch('database.get_user') as mock_db:
        mock_db.return_value = None  ***REMOVED*** User not found

        with pytest.raises(ResourceNotFoundException) as exc_info:
            await get_user_profile(123)

        assert "User with ID 123 not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404
```

***REMOVED******REMOVED******REMOVED*** Test Optional Operations

```python
async def test_optional_operation_graceful_degradation():
    """Optional operations should return fallback values on failure."""
    with patch('recommendation_api.get_similar') as mock_api:
        mock_api.side_effect = ConnectionError("Service unavailable")

        result = await get_movie_recommendations(123)

        assert result == []  ***REMOVED*** Fallback value
        ***REMOVED*** No exception raised

async def test_optional_operation_success():
    """Optional operations should work normally when service is available."""
    with patch('recommendation_api.get_similar') as mock_api:
        mock_api.return_value = [{"id": 1, "title": "Similar Movie"}]

        result = await get_movie_recommendations(123)

        assert len(result) == 1
        assert result[0]["title"] == "Similar Movie"
```

***REMOVED******REMOVED******REMOVED*** Test Error Mapping

```python
async def test_error_mapping_auth_failures():
    """Authentication errors should be mapped to semantic exceptions."""
    test_cases = [
        ("invalid_credentials", AuthenticationException, "Invalid email or password"),
        ("account_locked", AuthenticationException, "Account temporarily locked"),
        ("token_expired", AuthenticationException, "Session expired"),
    ]

    for error_key, expected_exception, expected_message in test_cases:
        with patch('auth_service.validate_token') as mock_auth:
            mock_auth.side_effect = ValueError(error_key)

            with pytest.raises(expected_exception) as exc_info:
                await validate_user_session("fake-token")

            assert expected_message in str(exc_info.value)
```

***REMOVED******REMOVED*** 📊 Monitoring and Observability

***REMOVED******REMOVED******REMOVED*** Essential Metrics

```python
***REMOVED*** Error rate by service and operation
error_rate = Counter('service_errors_total', ['service', 'operation', 'error_type'])

***REMOVED*** Graceful degradation tracking
degradation_count = Counter('graceful_degradations_total', ['service', 'operation'])

***REMOVED*** Critical service availability
critical_service_uptime = Gauge('critical_service_availability', ['service'])
```

***REMOVED******REMOVED******REMOVED*** Log Structure Standards

```python
***REMOVED*** Structured logging for error context
logger.error(
    "Critical service failure",
    extra={
        "service": "user-database",
        "operation": "get_user_profile",
        "user_id": user_id,
        "error_type": "ExternalServiceException",
        "duration_ms": 1500,
        "retry_count": 3,
        "original_error": str(original_exception)
    }
)
```

***REMOVED******REMOVED******REMOVED*** Alert Definitions

```yaml
***REMOVED*** Critical service failure alerts
- alert: CriticalServiceDown
  expr: rate(service_errors_total{error_type="ExternalServiceException"}[5m]) > 0.1
  labels:
    severity: critical
  annotations:
    summary: "Critical service {{ $labels.service }} failing"

***REMOVED*** Excessive graceful degradation
- alert: HighGracefulDegradation
  expr: rate(graceful_degradations_total[15m]) > 50
  labels:
    severity: warning
  annotations:
    summary: "High rate of graceful degradation in {{ $labels.service }}"
```

***REMOVED******REMOVED*** 🔒 Security Considerations

***REMOVED******REMOVED******REMOVED*** Error Information Disclosure

```python
***REMOVED*** ❌ Bad: Exposing internal details
@service_error_handler("database", logger)
async def get_user_secrets(user_id: int):
    try:
        return await db.query("SELECT * FROM secrets WHERE user_id = ?", user_id)
    except Exception as e:
        ***REMOVED*** Exposes database structure in error messages
        raise HTTPException(500, f"Database error: {str(e)}")

***REMOVED*** ✅ Good: Generic error messages for security
@critical_service_handler("database", logger)
async def get_user_secrets(user_id: int):
    ***REMOVED*** Error details logged internally, generic message to user
    return await db.get_user_secrets(user_id)
```

***REMOVED******REMOVED******REMOVED*** Authentication Error Timing

```python
***REMOVED*** ❌ Bad: Different timing reveals user existence
async def authenticate_user(email: str, password: str):
    user = await get_user_by_email(email)  ***REMOVED*** Fast if user doesn't exist
    if not user:
        raise AuthenticationException("Invalid credentials")

    if not verify_password(password, user.hashed_password):  ***REMOVED*** Slow hash check
        raise AuthenticationException("Invalid credentials")

***REMOVED*** ✅ Good: Consistent timing
async def authenticate_user(email: str, password: str):
    user = await get_user_by_email(email)
    dummy_hash = "$2b$12$dummy_hash_for_timing_consistency"

    if user:
        is_valid = verify_password(password, user.hashed_password)
    else:
        ***REMOVED*** Still perform hash to maintain consistent timing
        verify_password(password, dummy_hash)
        is_valid = False

    if not is_valid:
        raise AuthenticationException("Invalid credentials")
```

***REMOVED******REMOVED*** 🚀 Performance Considerations

***REMOVED******REMOVED******REMOVED*** Timeout Configuration

```python
***REMOVED*** Configure appropriate timeouts for different service types
@critical_service_handler("database", logger)
async def get_user_data(user_id: int):
    ***REMOVED*** Fast database operations - short timeout
    async with timeout(5):  ***REMOVED*** 5 seconds
        return await db.get_user(user_id)

@optional_service_handler("external-api", logger, fallback_value=[])
async def get_enrichment_data():
    ***REMOVED*** External API - longer timeout before fallback
    async with timeout(15):  ***REMOVED*** 15 seconds
        return await external_api.get_data()
```

***REMOVED******REMOVED******REMOVED*** Circuit Breaker Integration

```python
from circuit_breaker import CircuitBreaker

***REMOVED*** Circuit breaker for optional services
@optional_service_handler("recommendation-api", logger, fallback_value=[])
@CircuitBreaker(failure_threshold=5, reset_timeout=60)
async def get_recommendations():
    return await reco_api.get_similar()
```

***REMOVED******REMOVED*** 📚 Additional Resources

- [Migration Guide](./MIGRATION_GUIDE.md) - Step-by-step migration instructions
- [Enhanced Error Handling](./ENHANCED_ERROR_HANDLING.md) - Technical documentation
- [Examples](../examples/error_handling_demo.py) - Working code examples
- [Adoption Strategy](./ADOPTION_STRATEGY.md) - Rollout planning

---

Following these best practices ensures consistent, maintainable, and observable error handling across the Next Watch platform. The patterns provide a foundation for reliable service interactions while maintaining excellent user experience.
