# Enhanced Error Handling Training Guide

## Overview

This training guide provides hands-on exercises and practical examples for mastering the enhanced error handling system. It's designed for developers who need to understand and implement the patterns across Next Watch services.

## 🎯 Learning Objectives

By the end of this training, you will be able to:

1. **Choose the right decorator** for different types of operations
2. **Implement semantic error preservation** for business logic
3. **Configure graceful degradation** for optional services
4. **Write comprehensive tests** for error scenarios
5. **Set up monitoring and observability** for error tracking
6. **Debug and troubleshoot** error handling issues

## 📚 Prerequisites

- Python 3.8+
- FastAPI knowledge
- Basic understanding of microservices
- Familiarity with async/await
- pytest experience

## 🧪 Lab Environment Setup

### Step 1: Install Dependencies

```bash
# In your service directory
pip install fast-core pytest pytest-asyncio httpx
```

### Step 2: Basic Service Setup

Create a sample service for practice:

```python
# training_service.py
from typing import Optional, List, Dict, Any
import asyncio
import random
from fastapi import FastAPI, HTTPException
from fast_core.errors import (
    critical_service_handler,
    optional_service_handler,
    service_error_handler,
    ValidationException,
    AuthenticationException,
    ResourceNotFoundException,
)
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Error Handling Training Service")

# Simulated external services
class DatabaseService:
    async def get_user(self, user_id: int) -> Optional[Dict]:
        await asyncio.sleep(0.1)  # Simulate DB latency
        if user_id <= 0:
            raise ValueError("Invalid user ID")
        if user_id == 999:  # Simulate user not found
            return None
        if user_id == 500:  # Simulate database error
            raise ConnectionError("Database connection failed")
        return {"id": user_id, "name": f"User {user_id}"}

class RecommendationService:
    async def get_similar_items(self, item_id: int) -> List[Dict]:
        await asyncio.sleep(0.2)  # Simulate API latency
        if random.random() < 0.3:  # 30% chance of failure
            raise ConnectionError("Recommendation service unavailable")
        return [{"id": i, "title": f"Recommendation {i}"} for i in range(3)]

class AuthService:
    async def authenticate(self, token: str) -> Optional[Dict]:
        await asyncio.sleep(0.05)
        if token == "invalid":
            raise ValueError("invalid_credentials")
        if token == "expired":
            raise ValueError("token_expired")
        if token == "locked":
            raise ValueError("account_locked")
        if token == "error":
            raise ConnectionError("Auth service down")
        return {"user_id": 123, "email": "user@example.com"}

# Service instances
db_service = DatabaseService()
reco_service = RecommendationService()
auth_service = AuthService()
```

## 🏋️ Exercise 1: Critical Service Handler

**Objective**: Learn when and how to use `@critical_service_handler`

### Task 1.1: Basic Critical Operation

Implement a user retrieval function that must always work:

```python
# TODO: Add the appropriate decorator
async def get_user_profile(user_id: int) -> Dict[str, Any]:
    """Get user profile - critical for app functionality."""
    # TODO: Add input validation
    # TODO: Call db_service.get_user(user_id)
    # TODO: Handle case when user is not found
    pass
```

<details>
<summary>Solution 1.1</summary>

```python
@critical_service_handler("database", logger)
async def get_user_profile(user_id: int) -> Dict[str, Any]:
    """Get user profile - critical for app functionality."""
    if user_id <= 0:
        raise ValidationException("User ID must be positive")

    user = await db_service.get_user(user_id)
    if not user:
        raise ResourceNotFoundException(
            detail=f"User with ID {user_id} not found",
            resource_type="User",
            resource_id=str(user_id)
        )
    return user
```

</details>

### Task 1.2: Add FastAPI Endpoint

Create a FastAPI endpoint that uses your critical function:

```python
@app.get("/users/{user_id}")
async def get_user_endpoint(user_id: int):
    """Get user profile endpoint."""
    # TODO: Call get_user_profile and return the result
    pass
```

<details>
<summary>Solution 1.2</summary>

```python
@app.get("/users/{user_id}")
async def get_user_endpoint(user_id: int):
    """Get user profile endpoint."""
    return await get_user_profile(user_id)
```

</details>

### Test Your Implementation

```python
# test_exercise_1.py
import pytest
from unittest.mock import patch, AsyncMock
from fast_core.errors import ValidationException, ResourceNotFoundException, ExternalServiceException

@pytest.mark.asyncio
async def test_get_user_profile_success():
    """Test successful user retrieval."""
    result = await get_user_profile(123)
    assert result["id"] == 123
    assert result["name"] == "User 123"

@pytest.mark.asyncio
async def test_get_user_profile_validation_error():
    """Test validation error for invalid user ID."""
    with pytest.raises(ValidationException) as exc_info:
        await get_user_profile(-1)
    assert "positive" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_user_profile_not_found():
    """Test user not found scenario."""
    with pytest.raises(ResourceNotFoundException) as exc_info:
        await get_user_profile(999)
    assert "not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_user_profile_database_failure():
    """Test database failure scenario."""
    with pytest.raises(ExternalServiceException) as exc_info:
        await get_user_profile(500)
    assert exc_info.value.status_code == 502
```

Run the tests:

```bash
pytest test_exercise_1.py -v
```

## 🏋️ Exercise 2: Optional Service Handler

**Objective**: Learn graceful degradation for non-critical services

### Task 2.1: Implement Recommendation Function

Create a recommendation function that gracefully degrades:

```python
# TODO: Add the appropriate decorator with fallback
async def get_item_recommendations(item_id: int) -> List[Dict[str, Any]]:
    """Get recommendations - nice to have but not essential."""
    # TODO: Add input validation
    # TODO: Call reco_service.get_similar_items(item_id)
    pass
```

<details>
<summary>Solution 2.1</summary>

```python
@optional_service_handler(
    service_name="recommendation-api",
    logger=logger,
    fallback_value=[]
)
async def get_item_recommendations(item_id: int) -> List[Dict[str, Any]]:
    """Get recommendations - nice to have but not essential."""
    if item_id <= 0:
        raise ValidationException("Item ID must be positive")

    return await reco_service.get_similar_items(item_id)
```

</details>

### Task 2.2: Create Composite Endpoint

Build an endpoint that combines critical and optional data:

```python
@app.get("/items/{item_id}/details")
async def get_item_details(item_id: int):
    """Get item details with optional recommendations."""
    # TODO: Get user profile (critical)
    # TODO: Get recommendations (optional)
    # TODO: Return combined response
    pass
```

<details>
<summary>Solution 2.2</summary>

```python
@app.get("/items/{item_id}/details")
async def get_item_details(item_id: int):
    """Get item details with optional recommendations."""
    # Critical: Basic user data (reusing user_id as item_id for simplicity)
    user = await get_user_profile(item_id)

    # Optional: Recommendations (will be empty list if service fails)
    recommendations = await get_item_recommendations(item_id)

    return {
        "user": user,
        "recommendations": recommendations,
        "has_recommendations": len(recommendations) > 0
    }
```

</details>

### Test Graceful Degradation

```python
# test_exercise_2.py
@pytest.mark.asyncio
async def test_recommendations_success():
    """Test successful recommendation retrieval."""
    # May succeed or fail due to random behavior - that's the point!
    result = await get_item_recommendations(123)
    assert isinstance(result, list)

@pytest.mark.asyncio
async def test_recommendations_graceful_degradation():
    """Test graceful degradation with mocked failure."""
    with patch('training_service.reco_service.get_similar_items') as mock_reco:
        mock_reco.side_effect = ConnectionError("Service down")

        result = await get_item_recommendations(123)
        assert result == []  # Fallback value

@pytest.mark.asyncio
async def test_item_details_with_recommendations():
    """Test composite endpoint with working recommendations."""
    result = await get_item_details(123)

    assert "user" in result
    assert "recommendations" in result
    assert "has_recommendations" in result
    assert result["user"]["id"] == 123
```

## 🏋️ Exercise 3: Custom Error Mapping

**Objective**: Learn to preserve business logic semantics

### Task 3.1: Authentication with Error Mapping

Implement authentication with semantic error preservation:

```python
# TODO: Add service_error_handler with custom error mapping
async def authenticate_user(token: str) -> Dict[str, Any]:
    """Authenticate user with semantic error mapping."""
    # TODO: Add input validation
    # TODO: Call auth_service.authenticate(token)
    # TODO: Handle None result appropriately
    pass
```

<details>
<summary>Solution 3.1</summary>

```python
@service_error_handler(
    service_name="auth-service",
    logger=logger,
    preserve_semantics=True,
    error_mapping={
        "invalid_credentials": lambda e: AuthenticationException("Invalid token"),
        "token_expired": lambda e: AuthenticationException("Token has expired"),
        "account_locked": lambda e: AuthenticationException("Account is locked"),
    }
)
async def authenticate_user(token: str) -> Dict[str, Any]:
    """Authenticate user with semantic error mapping."""
    if not token or not token.strip():
        raise ValidationException("Token is required")

    user = await auth_service.authenticate(token.strip())
    if not user:
        raise ValueError("invalid_credentials")

    return user
```

</details>

### Task 3.2: Protected Endpoint

Create an endpoint that requires authentication:

```python
@app.get("/protected")
async def protected_endpoint(authorization: str = None):
    """Protected endpoint requiring authentication."""
    # TODO: Extract token from authorization header
    # TODO: Authenticate user
    # TODO: Return protected data
    pass
```

<details>
<summary>Solution 3.2</summary>

```python
@app.get("/protected")
async def protected_endpoint(authorization: str = None):
    """Protected endpoint requiring authentication."""
    if not authorization or not authorization.startswith("Bearer "):
        raise ValidationException("Authorization header required")

    token = authorization.replace("Bearer ", "")
    user = await authenticate_user(token)

    return {
        "message": "Access granted",
        "user": user,
        "protected_data": "This is sensitive information"
    }
```

</details>

### Test Error Mapping

```python
# test_exercise_3.py
@pytest.mark.asyncio
async def test_authentication_success():
    """Test successful authentication."""
    result = await authenticate_user("valid_token")
    assert result["user_id"] == 123

@pytest.mark.asyncio
async def test_authentication_invalid_credentials():
    """Test invalid credentials mapping."""
    with pytest.raises(AuthenticationException) as exc_info:
        await authenticate_user("invalid")
    assert "Invalid token" in str(exc_info.value)

@pytest.mark.asyncio
async def test_authentication_expired_token():
    """Test expired token mapping."""
    with pytest.raises(AuthenticationException) as exc_info:
        await authenticate_user("expired")
    assert "expired" in str(exc_info.value)

@pytest.mark.asyncio
async def test_authentication_service_failure():
    """Test auth service failure."""
    with pytest.raises(ExternalServiceException) as exc_info:
        await authenticate_user("error")
    assert exc_info.value.status_code == 502
```

## 🏋️ Exercise 4: Real-World Scenario

**Objective**: Combine all patterns in a realistic scenario

### Task 4.1: Movie Service Implementation

Build a movie service that demonstrates all patterns:

```python
class MovieService:
    def __init__(self):
        self.db = DatabaseService()
        self.reco = RecommendationService()
        self.auth = AuthService()

    # TODO: Implement get_movie (critical)
    async def get_movie(self, movie_id: int) -> Dict[str, Any]:
        pass

    # TODO: Implement get_movie_recommendations (optional)
    async def get_movie_recommendations(self, movie_id: int) -> List[Dict[str, Any]]:
        pass

    # TODO: Implement get_movie_for_user (authentication + optional features)
    async def get_movie_for_user(self, movie_id: int, token: str) -> Dict[str, Any]:
        pass

movie_service = MovieService()
```

<details>
<summary>Solution 4.1</summary>

```python
class MovieService:
    def __init__(self):
        self.db = DatabaseService()
        self.reco = RecommendationService()
        self.auth = AuthService()

    @critical_service_handler("database", logger)
    async def get_movie(self, movie_id: int) -> Dict[str, Any]:
        """Get movie data - critical operation."""
        if movie_id <= 0:
            raise ValidationException("Movie ID must be positive")

        movie = await self.db.get_user(movie_id)  # Reusing user service as movie service
        if not movie:
            raise ResourceNotFoundException(
                detail=f"Movie with ID {movie_id} not found",
                resource_type="Movie",
                resource_id=str(movie_id)
            )
        return {"id": movie["id"], "title": f"Movie {movie['id']}", "description": "A great movie"}

    @optional_service_handler(
        service_name="recommendation-api",
        logger=logger,
        fallback_value=[]
    )
    async def get_movie_recommendations(self, movie_id: int) -> List[Dict[str, Any]]:
        """Get movie recommendations - optional enhancement."""
        if movie_id <= 0:
            raise ValidationException("Movie ID must be positive")

        return await self.reco.get_similar_items(movie_id)

    @service_error_handler(
        service_name="auth-service",
        logger=logger,
        preserve_semantics=True,
        error_mapping={
            "invalid_credentials": lambda e: AuthenticationException("Invalid token"),
            "token_expired": lambda e: AuthenticationException("Token has expired"),
        }
    )
    async def get_movie_for_user(self, movie_id: int, token: str) -> Dict[str, Any]:
        """Get movie with user-specific data and recommendations."""
        # Authenticate user first
        if not token:
            raise ValidationException("Authentication token required")

        user = await self.auth.authenticate(token)
        if not user:
            raise ValueError("invalid_credentials")

        # Get core movie data (critical)
        movie = await self.get_movie(movie_id)

        # Get recommendations (optional)
        recommendations = await self.get_movie_recommendations(movie_id)

        return {
            "movie": movie,
            "user": user,
            "recommendations": recommendations,
            "personalized": True
        }

movie_service = MovieService()
```

</details>

### Task 4.2: Complete API Endpoints

```python
@app.get("/movies/{movie_id}")
async def get_movie_endpoint(movie_id: int):
    """Public movie endpoint."""
    return await movie_service.get_movie(movie_id)

@app.get("/movies/{movie_id}/personalized")
async def get_personalized_movie(movie_id: int, authorization: str = None):
    """Personalized movie endpoint."""
    if not authorization or not authorization.startswith("Bearer "):
        raise ValidationException("Authorization header required")

    token = authorization.replace("Bearer ", "")
    return await movie_service.get_movie_for_user(movie_id, token)
```

### Comprehensive Testing

```python
# test_exercise_4.py
@pytest.mark.asyncio
async def test_movie_service_success():
    """Test successful movie retrieval."""
    result = await movie_service.get_movie(123)
    assert result["id"] == 123
    assert "title" in result

@pytest.mark.asyncio
async def test_personalized_movie_success():
    """Test personalized movie with valid token."""
    result = await movie_service.get_movie_for_user(123, "valid_token")
    assert "movie" in result
    assert "user" in result
    assert "recommendations" in result
    assert result["personalized"] is True

@pytest.mark.asyncio
async def test_personalized_movie_auth_failure():
    """Test personalized movie with invalid token."""
    with pytest.raises(AuthenticationException):
        await movie_service.get_movie_for_user(123, "invalid")

@pytest.mark.asyncio
async def test_graceful_degradation_in_personalized():
    """Test that recommendation failures don't break personalized endpoint."""
    with patch('training_service.reco_service.get_similar_items') as mock_reco:
        mock_reco.side_effect = ConnectionError("Recommendations down")

        result = await movie_service.get_movie_for_user(123, "valid_token")

        # Core functionality still works
        assert "movie" in result
        assert "user" in result
        # Recommendations gracefully degrade
        assert result["recommendations"] == []
```

## 🏋️ Exercise 5: Monitoring and Observability

**Objective**: Learn to monitor and debug error handling

### Task 5.1: Add Custom Metrics

```python
from prometheus_client import Counter, Histogram, generate_latest

# TODO: Create metrics for tracking errors
error_counter = Counter('service_errors_total', 'Total service errors', ['service', 'error_type'])
degradation_counter = Counter('graceful_degradations_total', 'Graceful degradations', ['service'])
operation_duration = Histogram('operation_duration_seconds', 'Operation duration', ['operation'])

# TODO: Add metrics endpoint
@app.get("/metrics")
async def metrics():
    return generate_latest()
```

### Task 5.2: Enhanced Logging

```python
import structlog

# Configure structured logging
logger = structlog.get_logger()

# TODO: Add logging to your service methods
# Example for movie service:
async def get_movie_with_logging(movie_id: int) -> Dict[str, Any]:
    start_time = time.time()

    logger.info(
        "Getting movie",
        operation="get_movie",
        movie_id=movie_id
    )

    try:
        result = await movie_service.get_movie(movie_id)
        duration = time.time() - start_time

        logger.info(
            "Movie retrieved successfully",
            operation="get_movie",
            movie_id=movie_id,
            duration=duration
        )

        operation_duration.labels(operation="get_movie").observe(duration)
        return result

    except Exception as e:
        duration = time.time() - start_time

        logger.error(
            "Movie retrieval failed",
            operation="get_movie",
            movie_id=movie_id,
            duration=duration,
            error=str(e),
            error_type=type(e).__name__
        )

        error_counter.labels(
            service="movie-service",
            error_type=type(e).__name__
        ).inc()

        raise
```

## 🧩 Challenge Exercises

### Challenge 1: Circuit Breaker Integration

Implement a circuit breaker pattern with the error handling decorators:

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    # TODO: Implement circuit breaker logic
    # TODO: Integrate with optional_service_handler
```

### Challenge 2: Retry Strategy

Add intelligent retry logic to your error handlers:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

# TODO: Combine tenacity retry with error handling decorators
# TODO: Implement different retry strategies for different error types
```

### Challenge 3: Error Rate Limiting

Implement error rate limiting to prevent cascading failures:

```python
# TODO: Track error rates per service
# TODO: Implement backoff when error rates are high
# TODO: Integrate with graceful degradation
```

## 📝 Assessment Questions

### Knowledge Check

1. **When should you use `@critical_service_handler` vs `@optional_service_handler`?**

2. **What happens when you use `@optional_service_handler` without a `fallback_value`?**

3. **How does `preserve_semantics=True` affect error handling?**

4. **What's the difference between business logic errors and infrastructure errors?**

5. **How should you handle authentication errors in a multi-service architecture?**

### Practical Scenarios

**Scenario 1**: You have a product page that shows:

- Product details (essential)
- Reviews (important but not critical)
- Recommendations (nice to have)
- Social media feeds (optional)

How would you classify and handle errors for each component?

**Scenario 2**: Your payment service can return these errors:

- Invalid card number
- Insufficient funds
- Card expired
- Payment processor down
- Network timeout

How would you map these to appropriate HTTP status codes and user messages?

## 🎓 Graduation Project

### Build a Complete Service

Create a realistic service that demonstrates all error handling patterns:

1. **User Management Service** with:

   - User registration (critical)
   - User profile updates (critical)
   - Activity tracking (optional)
   - Recommendation updates (optional)

2. **Requirements**:

   - Use all three decorator types appropriately
   - Implement comprehensive error mapping
   - Add proper validation and business logic
   - Include monitoring and logging
   - Write complete test suite
   - Document error handling decisions

3. **Deliverables**:
   - Working FastAPI service
   - Comprehensive test suite (>90% coverage)
   - Error handling documentation
   - Monitoring dashboard config
   - Performance benchmarks

## 📚 Additional Resources

### Documentation

- [Migration Guide](./MIGRATION_GUIDE.md)
- [Best Practices](./ERROR_HANDLING_BEST_PRACTICES.md)
- [Enhanced Error Handling](./ENHANCED_ERROR_HANDLING.md)

### Examples

- [Working demos](../examples/error_handling_demo.py)
- [Service implementations](../../apps/*/src/*/services/)
- [Test patterns](../../apps/*/tests/)

### Tools

- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [httpx](https://www.python-httpx.org/)
- [structlog](https://www.structlog.org/)
- [prometheus-client](https://github.com/prometheus/client_python)

## 🆘 Getting Help

### Common Issues

1. **Import Errors**: Ensure fast-core is properly installed
2. **Circular Imports**: Move router imports to function level
3. **Type Errors**: Check decorator return type compatibility
4. **Test Failures**: Verify mock configurations match expected error types

### Support Channels

1. Check examples in `libs/fast-core/examples/`
2. Review working implementations in service directories
3. Consult the troubleshooting sections in other guides
4. Create issues for complex migration questions

---

This training guide provides a comprehensive foundation for mastering enhanced error handling. Practice each exercise thoroughly and apply the patterns consistently across your services.
