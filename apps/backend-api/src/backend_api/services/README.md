# Backend API Services Module

The `services` module contains business logic and service classes for the Next Watch Backend API, following Clean Architecture principles and the CQRS pattern to separate command operations from query operations.

## Architecture Overview

The services module is organized around domain-specific service classes:

```
services/
├── __init__.py           # Module exports and optional imports
├── health_service.py     # Health monitoring service
├── movie_service.py      # Movie-related business logic
├── user_interaction.py   # User interaction and social features
├── suggestion_engine.py  # Redis-based recommendation engine (optional)
└── auth.py              # Authentication and authorization
```

## Core Principles

### Clean Architecture

- **Domain Logic**: Business rules are encapsulated in service classes
- **Dependency Inversion**: Services depend on abstractions, not concrete implementations
- **Single Responsibility**: Each service has a clearly defined purpose

### CQRS Pattern

- **Command Operations**: State-changing operations (create, update, delete)
- **Query Operations**: Read-only operations with optimized data access
- **Separation**: Clear distinction between commands and queries

## Services Overview

### Health Service (`health_service.py`)

Comprehensive health monitoring for all system dependencies.

#### Features

- **Multi-Service Monitoring**: PostgreSQL and Redis health checks
- **Concurrent Execution**: Health checks run in parallel for performance
- **Detailed Reporting**: Response times, connection details, and error information
- **Graceful Fallback**: Continues operation even if some checks fail
- **Synchronous Support**: Both async and sync health check methods

#### Health Check Components

```python
@dataclass
class HealthCheckResult:
    is_healthy: bool
    status: str
    response_time_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

#### Usage

```python
from backend_api.services.health_service import get_health_service

# Get global health service instance
health_service = get_health_service()

# Check all services
results = await health_service.check_all()

# Check individual services
postgres_result = health_service.check_postgres_sync()
redis_result = await health_service.check_redis()
```

#### PostgreSQL Health Check

- **Connection Test**: Establishes database connection
- **Query Execution**: Runs simple test query
- **Version Information**: Retrieves PostgreSQL version
- **Database Size**: Reports current database size
- **Response Time**: Measures connection and query time

#### Redis Health Check

- **Connection Pool**: Uses configured Redis connection settings
- **Ping Test**: Verifies Redis connectivity
- **Server Information**: Retrieves Redis server stats
- **Performance Metrics**: Memory usage, command counts, hit/miss ratios
- **Connection Details**: Client count and uptime information

#### Global Instance Management

```python
# Singleton pattern for resource efficiency
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

### Movie Service (`movie_service.py`)

Business logic for movie-related operations.

#### Features

- **Movie Search**: Advanced search with filters and pagination
- **Movie Details**: Comprehensive movie information retrieval
- **Genre Management**: Genre-based categorization and filtering
- **Rating Integration**: Integration with rating and review systems

### User Interaction Service (`user_interaction.py`)

Handles user interactions and social features.

#### Features

- **User Profiles**: Profile management and preferences
- **Social Interactions**: Following, likes, and social features
- **Activity Tracking**: User activity logging and analytics
- **Recommendation Input**: Provides data for recommendation algorithms

### Suggestion Engine (`suggestion_engine.py`)

Redis-based recommendation and suggestion system.

#### Features

- **Real-time Recommendations**: Fast, cached recommendation delivery
- **User Preference Learning**: Adaptive recommendation algorithms
- **Content-Based Filtering**: Movie similarity recommendations
- **Collaborative Filtering**: User behavior-based recommendations
- **Performance Optimization**: Redis caching for sub-second response times

#### Optional Integration

```python
# Optional service with graceful fallback
try:
    from .suggestion_engine import SuggestionEngine
    _suggestion_engine_available = True
except ImportError:
    _suggestion_engine_available = False

if _suggestion_engine_available:
    __all__.append("SuggestionEngine")
```

### Authentication Service (`auth.py`)

User authentication and authorization logic.

#### Features

- **JWT Token Management**: Token generation and validation
- **User Registration**: Account creation and verification
- **Login/Logout**: Session management
- **Permission Control**: Role-based access control

## Integration with Core Module

### Health Service Integration

The health service is tightly integrated with the core application lifecycle:

#### Startup Integration

```python
# In core/app.py lifespan function
logger.info("Initializing health service")
try:
    health_service = HealthService()
    app.state.health_service = health_service
    logger.info("Health service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize health service: {e}")
    app.state.health_service = None
```

#### Route Integration

```python
# In routes/health.py
async def health_check(request: Request) -> JSONResponse:
    health_service = request.app.state.health_service
    if health_service:
        health_results = await health_service.check_all()
        # Process results...
    else:
        # Fallback to basic checks
        return await health_check_fallback()
```

#### Shutdown Integration

```python
# In core/app.py shutdown sequence
if hasattr(app.state, "health_service") and app.state.health_service is not None:
    try:
        logger.info("Shutting down health service")
        app.state.health_service.close()
        logger.info("Health service shut down successfully")
    except Exception as e:
        logger.error(f"Error shutting down health service: {e}")

# Close global health service
close_health_service()
```

## Configuration

Services are configured through the application settings:

### Database Configuration

```python
# PostgreSQL settings used by health service and other services
settings.database_url  # Connection string
```

### Redis Configuration

```python
# Redis settings for health service and suggestion engine
settings.redis_url                      # Connection URL
settings.redis_max_connections          # Connection pool size
settings.redis_socket_timeout           # Socket timeout
settings.redis_socket_connect_timeout   # Connection timeout
settings.redis_retry_on_timeout        # Retry behavior
```

## Error Handling

### Graceful Degradation

Services are designed to fail gracefully:

```python
# Health service continues if individual checks fail
if isinstance(postgres_result, Exception):
    results["postgres"] = HealthCheckResult(
        is_healthy=False, status="error", error=str(postgres_result)
    )
```

### Comprehensive Logging

```python
# Detailed error logging with context
logger.error(f"PostgreSQL health check failed: {e}")
logger.error(f"Redis health check failed: {e}", exc_info=True)
```

### Fallback Mechanisms

```python
# Fallback health checks when main service unavailable
if not hasattr(request.app.state, "health_service") or request.app.state.health_service is None:
    return await health_check_fallback()
```

## Testing

### Unit Testing

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
    # Additional assertions based on Redis availability
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_health_service_integration():
    health_service = HealthService()
    try:
        results = await health_service.check_all()
        assert "postgres" in results
        assert "redis" in results

        # Verify result structure
        for service_name, result in results.items():
            assert hasattr(result, "is_healthy")
            assert hasattr(result, "status")
            assert hasattr(result, "response_time_ms")
    finally:
        health_service.close()
```

### Mock Testing

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

## Performance Considerations

### Connection Management

- **Connection Reuse**: Health service reuses Redis connections
- **Connection Pooling**: Respects Redis connection pool settings
- **Resource Cleanup**: Proper connection cleanup during shutdown

### Concurrent Execution

```python
# Health checks run concurrently for better performance
postgres_task = asyncio.create_task(self.check_postgres())
redis_task = asyncio.create_task(self.check_redis())

postgres_result, redis_result = await asyncio.gather(
    postgres_task, redis_task, return_exceptions=True
)
```

### Caching Strategy

- **Global Instance**: Single health service instance reduces overhead
- **Connection Reuse**: Redis client connection is cached and reused
- **Efficient Queries**: Database queries are optimized for speed

## Monitoring and Observability

### Health Check Metrics

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

### Redis Monitoring

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

### Logging Integration

```python
# Structured logging for monitoring
logger.info("Health service initialized successfully")
logger.error(f"PostgreSQL health check failed: {e}")
logger.warning("Health service not available, using fallback health check")
```

## Security Considerations

### Database Security

- **Connection Security**: Uses secure database connections
- **Query Safety**: Uses parameterized queries to prevent injection
- **Error Handling**: Doesn't expose sensitive database information

### Redis Security

- **Connection Validation**: Validates Redis connections before use
- **Error Masking**: Masks sensitive Redis configuration in errors
- **Timeout Management**: Proper timeout handling prevents hanging connections

## Future Enhancements

### Planned Features

1. **Health Check Caching**: Cache health check results for high-frequency endpoints
2. **Circuit Breaker**: Implement circuit breaker pattern for external services
3. **Metrics Export**: Export health metrics to Prometheus/Grafana
4. **Alert Integration**: Integration with alerting systems
5. **Custom Checks**: Framework for custom health check plugins

### Service Expansion

1. **Message Queue Health**: RabbitMQ/Kafka health monitoring
2. **External API Health**: Third-party service health checks
3. **File System Health**: Disk space and file system monitoring
4. **Network Health**: Network connectivity and latency checks

### Performance Optimization

1. **Async Database Checks**: Full async database health checks
2. **Parallel Service Discovery**: Automatic service discovery and health checking
3. **Health Check Aggregation**: Intelligent health status aggregation
4. **Response Optimization**: Optimized health check response formats

## Dependencies

### Required Dependencies

- `sqlmodel`: Database ORM for PostgreSQL health checks
- `redis`: Redis client for cache health monitoring
- `asyncio`: Concurrent health check execution

### Optional Dependencies

- `asyncpg`: For async PostgreSQL health checks (planned)
- `prometheus_client`: For metrics export
- `aioredis`: For async Redis operations

The services module provides a comprehensive foundation for business logic with robust health monitoring, ensuring system reliability and observability in production environments.
