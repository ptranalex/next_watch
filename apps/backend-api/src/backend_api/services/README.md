***REMOVED*** Backend API Services Module

The `services` module contains business logic and service classes for the Next Watch Backend API, following Clean Architecture principles and the CQRS pattern to separate command operations from query operations.

***REMOVED******REMOVED*** Architecture Overview

The services module is organized around domain-specific service classes:

```
services/
├── __init__.py           ***REMOVED*** Module exports and optional imports
├── health_service.py     ***REMOVED*** Health monitoring service
├── movie_service.py      ***REMOVED*** Movie-related business logic
├── user_interaction.py   ***REMOVED*** User interaction and social features
├── suggestion_engine.py  ***REMOVED*** Redis-based recommendation engine (optional)
└── auth.py              ***REMOVED*** Authentication and authorization
```

***REMOVED******REMOVED*** Core Principles

***REMOVED******REMOVED******REMOVED*** Clean Architecture

- **Domain Logic**: Business rules are encapsulated in service classes
- **Dependency Inversion**: Services depend on abstractions, not concrete implementations
- **Single Responsibility**: Each service has a clearly defined purpose

***REMOVED******REMOVED******REMOVED*** CQRS Pattern

- **Command Operations**: State-changing operations (create, update, delete)
- **Query Operations**: Read-only operations with optimized data access
- **Separation**: Clear distinction between commands and queries

***REMOVED******REMOVED*** Services Overview

***REMOVED******REMOVED******REMOVED*** Health Service (`health_service.py`)

Comprehensive health monitoring for all system dependencies.

***REMOVED******REMOVED******REMOVED******REMOVED*** Features

- **Multi-Service Monitoring**: PostgreSQL and Redis health checks
- **Concurrent Execution**: Health checks run in parallel for performance
- **Detailed Reporting**: Response times, connection details, and error information
- **Graceful Fallback**: Continues operation even if some checks fail
- **Synchronous Support**: Both async and sync health check methods

***REMOVED******REMOVED******REMOVED******REMOVED*** Health Check Components

```python
@dataclass
class HealthCheckResult:
    is_healthy: bool
    status: str
    response_time_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Usage

```python
from backend_api.services.health_service import get_health_service

***REMOVED*** Get global health service instance
health_service = get_health_service()

***REMOVED*** Check all services
results = await health_service.check_all()

***REMOVED*** Check individual services
postgres_result = health_service.check_postgres_sync()
redis_result = await health_service.check_redis()
```

***REMOVED******REMOVED******REMOVED******REMOVED*** PostgreSQL Health Check

- **Connection Test**: Establishes database connection
- **Query Execution**: Runs simple test query
- **Version Information**: Retrieves PostgreSQL version
- **Database Size**: Reports current database size
- **Response Time**: Measures connection and query time

***REMOVED******REMOVED******REMOVED******REMOVED*** Redis Health Check

- **Connection Pool**: Uses configured Redis connection settings
- **Ping Test**: Verifies Redis connectivity
- **Server Information**: Retrieves Redis server stats
- **Performance Metrics**: Memory usage, command counts, hit/miss ratios
- **Connection Details**: Client count and uptime information

***REMOVED******REMOVED******REMOVED******REMOVED*** Global Instance Management

```python
***REMOVED*** Singleton pattern for resource efficiency
_health_service: Optional[HealthService] = None

def get_health_service() -> HealthService:
    """Get the global health service instance."""
    global _health_service
    if _health_service is None:
        _health_service = HealthService()
    return _health_service

def close_health_service() -> None:
    """Close the global health service instance."""
    global _health_service
    if _health_service is not None:
        _health_service.close()
        _health_service = None
```

***REMOVED******REMOVED******REMOVED*** Movie Service (`movie_service.py`)

Business logic for movie-related operations.

***REMOVED******REMOVED******REMOVED******REMOVED*** Features

- **Movie Search**: Advanced search with filters and pagination
- **Movie Details**: Comprehensive movie information retrieval
- **Genre Management**: Genre-based categorization and filtering
- **Rating Integration**: Integration with rating and review systems

***REMOVED******REMOVED******REMOVED*** User Interaction Service (`user_interaction.py`)

Handles user interactions and social features.

***REMOVED******REMOVED******REMOVED******REMOVED*** Features

- **User Profiles**: Profile management and preferences
- **Social Interactions**: Following, likes, and social features
- **Activity Tracking**: User activity logging and analytics
- **Recommendation Input**: Provides data for recommendation algorithms

***REMOVED******REMOVED******REMOVED*** Suggestion Engine (`suggestion_engine.py`)

Redis-based recommendation and suggestion system.

***REMOVED******REMOVED******REMOVED******REMOVED*** Features

- **Real-time Recommendations**: Fast, cached recommendation delivery
- **User Preference Learning**: Adaptive recommendation algorithms
- **Content-Based Filtering**: Movie similarity recommendations
- **Collaborative Filtering**: User behavior-based recommendations
- **Performance Optimization**: Redis caching for sub-second response times

***REMOVED******REMOVED******REMOVED******REMOVED*** Optional Integration

```python
***REMOVED*** Optional service with graceful fallback
try:
    from .suggestion_engine import SuggestionEngine
    _suggestion_engine_available = True
except ImportError:
    _suggestion_engine_available = False

if _suggestion_engine_available:
    __all__.append("SuggestionEngine")
```

***REMOVED******REMOVED******REMOVED*** Authentication Service (`auth.py`)

User authentication and authorization logic.

***REMOVED******REMOVED******REMOVED******REMOVED*** Features

- **JWT Token Management**: Token generation and validation
- **User Registration**: Account creation and verification
- **Login/Logout**: Session management
- **Permission Control**: Role-based access control

***REMOVED******REMOVED*** Integration with Core Module

***REMOVED******REMOVED******REMOVED*** Health Service Integration

The health service is tightly integrated with the core application lifecycle:

***REMOVED******REMOVED******REMOVED******REMOVED*** Startup Integration

```python
***REMOVED*** In core/app.py lifespan function
logger.info("Initializing health service")
try:
    health_service = HealthService()
    app.state.health_service = health_service
    logger.info("Health service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize health service: {e}")
    app.state.health_service = None
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Route Integration

```python
***REMOVED*** In routes/health.py
async def health_check(request: Request) -> JSONResponse:
    health_service = request.app.state.health_service
    if health_service:
        health_results = await health_service.check_all()
        ***REMOVED*** Process results...
    else:
        ***REMOVED*** Fallback to basic checks
        return await health_check_fallback()
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Shutdown Integration

```python
***REMOVED*** In core/app.py shutdown sequence
if hasattr(app.state, "health_service") and app.state.health_service is not None:
    try:
        logger.info("Shutting down health service")
        app.state.health_service.close()
        logger.info("Health service shut down successfully")
    except Exception as e:
        logger.error(f"Error shutting down health service: {e}")

***REMOVED*** Close global health service
close_health_service()
```

***REMOVED******REMOVED*** Configuration

Services are configured through the application settings:

***REMOVED******REMOVED******REMOVED*** Database Configuration

```python
***REMOVED*** PostgreSQL settings used by health service and other services
settings.database_url  ***REMOVED*** Connection string
```

***REMOVED******REMOVED******REMOVED*** Redis Configuration

```python
***REMOVED*** Redis settings for health service and suggestion engine
settings.redis_url                      ***REMOVED*** Connection URL
settings.redis_max_connections          ***REMOVED*** Connection pool size
settings.redis_socket_timeout           ***REMOVED*** Socket timeout
settings.redis_socket_connect_timeout   ***REMOVED*** Connection timeout
settings.redis_retry_on_timeout        ***REMOVED*** Retry behavior
```

***REMOVED******REMOVED*** Error Handling

***REMOVED******REMOVED******REMOVED*** Graceful Degradation

Services are designed to fail gracefully:

```python
***REMOVED*** Health service continues if individual checks fail
if isinstance(postgres_result, Exception):
    results["postgres"] = HealthCheckResult(
        is_healthy=False, status="error", error=str(postgres_result)
    )
```

***REMOVED******REMOVED******REMOVED*** Comprehensive Logging

```python
***REMOVED*** Detailed error logging with context
logger.error(f"PostgreSQL health check failed: {e}")
logger.error(f"Redis health check failed: {e}", exc_info=True)
```

***REMOVED******REMOVED******REMOVED*** Fallback Mechanisms

```python
***REMOVED*** Fallback health checks when main service unavailable
if not hasattr(request.app.state, "health_service") or request.app.state.health_service is None:
    return await health_check_fallback()
```

***REMOVED******REMOVED*** Testing

***REMOVED******REMOVED******REMOVED*** Unit Testing

```python
import pytest
from backend_api.services.health_service import HealthService

@pytest.fixture
def health_service():
    return HealthService()

@pytest.mark.asyncio
async def test_health_service_postgres(health_service):
    result = health_service.check_postgres_sync()
    assert isinstance(result.is_healthy, bool)
    assert result.status in ["healthy", "unhealthy"]
    assert result.response_time_ms is not None

@pytest.mark.asyncio
async def test_health_service_redis(health_service):
    result = await health_service.check_redis()
    assert isinstance(result.is_healthy, bool)
    ***REMOVED*** Additional assertions based on Redis availability
```

***REMOVED******REMOVED******REMOVED*** Integration Testing

```python
@pytest.mark.asyncio
async def test_health_service_integration():
    health_service = HealthService()
    try:
        results = await health_service.check_all()
        assert "postgres" in results
        assert "redis" in results

        ***REMOVED*** Verify result structure
        for service_name, result in results.items():
            assert hasattr(result, "is_healthy")
            assert hasattr(result, "status")
            assert hasattr(result, "response_time_ms")
    finally:
        health_service.close()
```

***REMOVED******REMOVED******REMOVED*** Mock Testing

```python
@pytest.fixture
def mock_redis_client(mocker):
    mock_client = mocker.Mock()
    mock_client.ping.return_value = True
    mock_client.info.return_value = {
        "redis_version": "7.0.0",
        "connected_clients": 1,
        "used_memory_human": "1M",
    }
    return mock_client

def test_redis_health_with_mock(mocker, mock_redis_client):
    mocker.patch("redis.Redis.from_url", return_value=mock_redis_client)
    health_service = HealthService()
    result = await health_service.check_redis()
    assert result.is_healthy is True
    assert result.details["version"] == "7.0.0"
```

***REMOVED******REMOVED*** Performance Considerations

***REMOVED******REMOVED******REMOVED*** Connection Management

- **Connection Reuse**: Health service reuses Redis connections
- **Connection Pooling**: Respects Redis connection pool settings
- **Resource Cleanup**: Proper connection cleanup during shutdown

***REMOVED******REMOVED******REMOVED*** Concurrent Execution

```python
***REMOVED*** Health checks run concurrently for better performance
postgres_task = asyncio.create_task(self.check_postgres())
redis_task = asyncio.create_task(self.check_redis())

postgres_result, redis_result = await asyncio.gather(
    postgres_task, redis_task, return_exceptions=True
)
```

***REMOVED******REMOVED******REMOVED*** Caching Strategy

- **Global Instance**: Single health service instance reduces overhead
- **Connection Reuse**: Redis client connection is cached and reused
- **Efficient Queries**: Database queries are optimized for speed

***REMOVED******REMOVED*** Monitoring and Observability

***REMOVED******REMOVED******REMOVED*** Health Check Metrics

Each health check provides detailed metrics:

```python
{
    "status": "healthy",
    "response_time_ms": 15.42,
    "details": {
        "version": "PostgreSQL 14.13",
        "database_size": "172 MB",
        "connection_successful": True
    }
}
```

***REMOVED******REMOVED******REMOVED*** Redis Monitoring

```python
{
    "status": "healthy",
    "response_time_ms": 8.33,
    "details": {
        "version": "7.2.5",
        "mode": "standalone",
        "connected_clients": 2,
        "used_memory_human": "4.65M",
        "uptime_in_days": 0,
        "keyspace_hits": 3578,
        "keyspace_misses": 0,
        "total_commands_processed": 7269
    }
}
```

***REMOVED******REMOVED******REMOVED*** Logging Integration

```python
***REMOVED*** Structured logging for monitoring
logger.info("Health service initialized successfully")
logger.error(f"PostgreSQL health check failed: {e}")
logger.warning("Health service not available, using fallback health check")
```

***REMOVED******REMOVED*** Security Considerations

***REMOVED******REMOVED******REMOVED*** Database Security

- **Connection Security**: Uses secure database connections
- **Query Safety**: Uses parameterized queries to prevent injection
- **Error Handling**: Doesn't expose sensitive database information

***REMOVED******REMOVED******REMOVED*** Redis Security

- **Connection Validation**: Validates Redis connections before use
- **Error Masking**: Masks sensitive Redis configuration in errors
- **Timeout Management**: Proper timeout handling prevents hanging connections

***REMOVED******REMOVED*** Future Enhancements

***REMOVED******REMOVED******REMOVED*** Planned Features

1. **Health Check Caching**: Cache health check results for high-frequency endpoints
2. **Circuit Breaker**: Implement circuit breaker pattern for external services
3. **Metrics Export**: Export health metrics to Prometheus/Grafana
4. **Alert Integration**: Integration with alerting systems
5. **Custom Checks**: Framework for custom health check plugins

***REMOVED******REMOVED******REMOVED*** Service Expansion

1. **Message Queue Health**: RabbitMQ/Kafka health monitoring
2. **External API Health**: Third-party service health checks
3. **File System Health**: Disk space and file system monitoring
4. **Network Health**: Network connectivity and latency checks

***REMOVED******REMOVED******REMOVED*** Performance Optimization

1. **Async Database Checks**: Full async database health checks
2. **Parallel Service Discovery**: Automatic service discovery and health checking
3. **Health Check Aggregation**: Intelligent health status aggregation
4. **Response Optimization**: Optimized health check response formats

***REMOVED******REMOVED*** Dependencies

***REMOVED******REMOVED******REMOVED*** Required Dependencies

- `sqlmodel`: Database ORM for PostgreSQL health checks
- `redis`: Redis client for cache health monitoring
- `asyncio`: Concurrent health check execution

***REMOVED******REMOVED******REMOVED*** Optional Dependencies

- `asyncpg`: For async PostgreSQL health checks (planned)
- `prometheus_client`: For metrics export
- `aioredis`: For async Redis operations

The services module provides a comprehensive foundation for business logic with robust health monitoring, ensuring system reliability and observability in production environments.
