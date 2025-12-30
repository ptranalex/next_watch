# Backend API Routes Module

The `routes` module contains all HTTP endpoints for the Next Watch Backend API, organized into logical router groups following FastAPI best practices.

## Architecture Overview

The routes module is organized around functional areas:

```
routes/
├── __init__.py       # Module initialization
├── api_v1/          # Versioned API routes (main business logic)
├── health.py        # Health check endpoints
├── meta.py          # Meta endpoints (root, debug)
└── ...              # Additional route modules
```

## Route Organization

### Meta Routes (`meta.py`)

Core application endpoints providing service information and debugging capabilities.

#### Root Endpoint (`/`)

**Description**: Main API information endpoint
**Method**: `GET`
**Authentication**: None required

**Response Structure**:

```json
{
  "message": "Welcome to Next Watch Backend API",
  "description": "Backend for Frontend API for serving movie data and user interactions",
  "api_versions": {
    "v1": "Available at /api/v1/"
  },
  "health_checks": {
    "comprehensive": "/health - Full health check with all dependencies",
    "liveness": "/health/live - Simple liveness check",
    "readiness": "/health/ready - Readiness check for critical dependencies",
    "database": "/db-health - Legacy database-only health check"
  },
  "documentation": "/docs",
  "features": [
    "Movie search and browsing",
    "User authentication and profiles",
    "Personalized recommendations",
    "Rating and review system",
    "Watchlist management",
    "Social features and interactions"
  ]
}
```

#### Debug Endpoint (`/debug`)

**Description**: Development and debugging information
**Method**: `GET`
**Authentication**: None required
**Environment**: Limited in production for security

**Development Response**:

```json
{
  "service": "backend-api",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2024-01-15T10:30:00",
  "debug": true,
  "log_level": "DEBUG",
  "api_port": 8000,
  "cors_origins": ["http://localhost:3000"],
  "performance_metrics_enabled": true,
  "database_masked": "postgresql://alex:****@localhost:5432/next_watch",
  "redis_url": "redis://localhost:6379/0",
  "redis_config": {
    "max_connections": 10,
    "socket_timeout": 30,
    "connect_timeout": 30,
    "retry_on_timeout": true
  }
}
```

**Production Response** (Limited):

```json
{
  "service": "backend-api",
  "version": "0.1.0",
  "environment": "production",
  "timestamp": "2024-01-15T10:30:00",
  "debug": false
}
```

### Health Routes (`health.py`)

Comprehensive health monitoring endpoints for system observability and load balancer integration.

#### Comprehensive Health Check (`/health`)

**Description**: Full health check of all system dependencies
**Method**: `GET`
**Authentication**: None required
**Use Case**: Detailed system monitoring and diagnostics

**Healthy Response** (200):

```json
{
  "status": "healthy",
  "service": "backend-api",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2024-01-15T10:30:00.123Z",
  "checks": {
    "postgres": {
      "status": "healthy",
      "healthy": true,
      "response_time_ms": 15.42,
      "details": {
        "version": "PostgreSQL 14.13 (Homebrew)",
        "database_size": "172 MB",
        "connection_successful": true,
        "query_result": 1
      }
    },
    "redis": {
      "status": "healthy",
      "healthy": true,
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
  }
}
```

**Unhealthy Response** (503):

```json
{
  "status": "unhealthy",
  "service": "backend-api",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2024-01-15T10:30:00.123Z",
  "checks": {
    "postgres": {
      "status": "healthy",
      "healthy": true,
      "response_time_ms": 12.34
    },
    "redis": {
      "status": "unhealthy",
      "healthy": false,
      "response_time_ms": 5000.0,
      "error": "Redis error: Connection timeout"
    }
  }
}
```

#### Liveness Check (`/health/live`)

**Description**: Simple liveness probe for container orchestrators
**Method**: `GET`
**Authentication**: None required
**Use Case**: Kubernetes/Docker liveness probes

**Response** (Always 200):

```json
{
  "status": "alive",
  "service": "backend-api",
  "version": "0.1.0",
  "timestamp": "2024-01-15T10:30:00.123Z"
}
```

#### Readiness Check (`/health/ready`)

**Description**: Readiness probe for critical dependencies
**Method**: `GET`
**Authentication**: None required
**Use Case**: Load balancer and orchestrator readiness checks

**Ready Response** (200):

```json
{
  "status": "ready",
  "service": "backend-api",
  "version": "0.1.0",
  "timestamp": "2024-01-15T10:30:00.123Z",
  "critical_services": {
    "postgres": true
  }
}
```

**Not Ready Response** (503):

```json
{
  "status": "not_ready",
  "service": "backend-api",
  "version": "0.1.0",
  "timestamp": "2024-01-15T10:30:00.123Z",
  "critical_services": {
    "postgres": false
  }
}
```

#### Legacy Database Health (`/db-health`)

**Description**: Legacy database-only health check
**Method**: `GET`
**Authentication**: None required
**Use Case**: Backward compatibility
**Note**: Use `/health` for comprehensive checks

**Healthy Response** (200):

```json
{
  "status": "ok",
  "result": 1,
  "db_type": "<class 'sqlmodel.engine.Session'>",
  "timestamp": "2024-01-15T10:30:00.123Z"
}
```

**Unhealthy Response** (503):

```json
{
  "status": "error",
  "error": "Connection failed",
  "trace": "Traceback...",
  "timestamp": "2024-01-15T10:30:00.123Z"
}
```

### API Routes (`api_v1/`)

Main business logic routes organized under versioned API structure.

**Base Path**: `/api/v1/`
**Description**: Core application functionality
**Authentication**: Varies by endpoint

## Health Check Integration

### Health Service Integration

Health endpoints integrate with the health service for comprehensive monitoring:

```python
async def health_check(request: Request) -> JSONResponse:
    # Get health service from application state
    health_service = request.app.state.health_service

    if health_service:
        # Use full health service capabilities
        health_results = await health_service.check_all()
        # Process and return results
    else:
        # Fallback to basic checks
        return await health_check_fallback()
```

### Fallback Mechanisms

When the health service is unavailable, fallback mechanisms ensure basic monitoring:

```python
async def health_check_fallback() -> JSONResponse:
    """Fallback health check when health service is not available."""
    try:
        # Use synchronous database check
        health_service = HealthService()
        postgres_result = health_service.check_postgres_sync()

        # Return simplified response
        return JSONResponse(
            status_code=200 if postgres_result.is_healthy else 503,
            content={
                "status": "healthy" if postgres_result.is_healthy else "unhealthy",
                "checks": {"postgres": postgres_result},
                "note": "Fallback health check - health service not initialized"
            }
        )
    except Exception as e:
        # Return error response
        return JSONResponse(status_code=503, content={"error": str(e)})
```

### Critical vs Non-Critical Services

Health checks distinguish between critical and non-critical services:

**Critical Services** (affect readiness):

- PostgreSQL database

**Non-Critical Services** (monitored but don't affect readiness):

- Redis cache

```python
# Readiness check only considers critical services
critical_services = ["postgres"]
critical_healthy = all(
    health_results[service].is_healthy
    for service in critical_services
    if service in health_results
)
```

## Error Handling

### Global Exception Handling

Routes benefit from global exception handling in the core module:

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
```

### Specific Error Responses

Health endpoints provide specific error information:

```python
# Service unavailable with details
return JSONResponse(
    status_code=503,
    content={
        "status": "error",
        "service": "backend-api",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "error": f"Health check failed: {str(e)}",
        "checks": {
            "postgres": {"status": "unknown", "healthy": False},
            "redis": {"status": "unknown", "healthy": False}
        }
    }
)
```

## Response Standards

### Common Response Structure

All endpoints follow consistent response patterns:

```python
{
    "status": "success|error|healthy|unhealthy|alive|ready|not_ready",
    "service": "backend-api",
    "version": "0.1.0",
    "timestamp": "2024-01-15T10:30:00.123Z",
    # Endpoint-specific data
}
```

### HTTP Status Codes

**Health Endpoints**:

- `200`: Service healthy/ready/alive
- `503`: Service unhealthy/not ready

**Meta Endpoints**:

- `200`: Success
- `403`: Forbidden (debug endpoint in production)
- `500`: Internal server error

### Content Types

All endpoints return `application/json` with UTF-8 encoding.

## Load Balancer Integration

### Health Check Endpoints for Load Balancers

**Liveness Probe**: `/health/live`

- **Purpose**: Determine if container should be restarted
- **Response**: Always returns 200 if service is running
- **Frequency**: High (every 10-30 seconds)

**Readiness Probe**: `/health/ready`

- **Purpose**: Determine if service should receive traffic
- **Response**: 200 if critical dependencies are healthy
- **Frequency**: Medium (every 30-60 seconds)

**Comprehensive Check**: `/health`

- **Purpose**: Detailed monitoring and diagnostics
- **Response**: Full dependency status with metrics
- **Frequency**: Low (every 5-10 minutes)

### Configuration Examples

**Kubernetes Configuration**:

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 30
```

**Docker Compose Configuration**:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Monitoring Integration

### Metrics Collection

Health endpoints provide metrics for monitoring systems:

- **Response Times**: Database and Redis response times
- **Connection Counts**: Active connections and pools
- **Error Rates**: Failed health check percentages
- **Resource Usage**: Memory, disk space, and network metrics

### Alerting Integration

Health check responses support alerting integration:

```python
# Alert on service unavailability
if not all_healthy:
    # Trigger alert with service details
    alert_data = {
        "service": "backend-api",
        "status": "unhealthy",
        "failed_checks": [
            service for service, result in health_results.items()
            if not result.is_healthy
        ]
    }
```

## Security Considerations

### Public Endpoints

Health and meta endpoints are publicly accessible for operational needs:

- No authentication required
- No sensitive information exposed
- Database credentials masked in debug output

### Information Disclosure

**Debug Endpoint**:

- Limited in production environment
- Sensitive configuration masked
- No user data exposed

**Health Endpoints**:

- Service status only (no data)
- Generic error messages
- No internal implementation details

## Testing

### Endpoint Testing

```python
import pytest
from fastapi.testclient import TestClient

def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to Next Watch Backend API"
    assert "api_versions" in data

def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "checks" in data

def test_liveness_endpoint(client: TestClient):
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_health_service_integration(client: TestClient):
    # Test with healthy services
    response = client.get("/health")
    assert response.status_code == 200

    # Test fallback mechanism
    # (Mock health service unavailability)
    response = client.get("/health")
    # Should still return a response
    assert response.status_code in [200, 503]
```

## Future Enhancements

### Planned Features

1. **Enhanced Metrics**: Prometheus metrics endpoint
2. **Custom Health Checks**: Plugin system for service-specific checks
3. **Health History**: Historical health data storage
4. **Alert Integration**: Direct integration with alerting systems
5. **Performance Benchmarks**: Performance regression detection

### API Versioning

1. **Version Strategy**: Semantic versioning for API endpoints
2. **Deprecation Handling**: Graceful deprecation of old endpoints
3. **Migration Tools**: Tools for API version migration

### Documentation

1. **OpenAPI Specification**: Complete API documentation
2. **Interactive Docs**: Enhanced FastAPI documentation
3. **Health Check Guide**: Comprehensive health monitoring guide

The routes module provides a well-structured, monitoring-friendly API surface with comprehensive health checking capabilities essential for production deployment.
