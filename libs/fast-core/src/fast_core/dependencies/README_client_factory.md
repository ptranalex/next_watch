# Service Client Factory Documentation

The Service Client Factory provides a comprehensive system for managing HTTP service clients in FastAPI applications with support for custom client types, singleton patterns, and automatic health checking.

## Quick Start

```python
from fast_core.dependencies.client_factory import register_service, get_service_client
from fastapi import FastAPI, Depends

# Register a service
register_service(
    name="user-service",
    base_url="https://api.users.com",
    timeout=30,
    singleton=True
)

# Create dependency
get_user_client = get_service_client("user-service")

# Use in endpoints
@app.get("/users/{user_id}")
async def get_user(user_id: int, client = Depends(get_user_client)):
    response = await client.get(f"/users/{user_id}")
    return response.json()
```

## Features

- **Service Registration**: Centralized configuration for external services
- **Custom Client Types**: Domain-specific client classes with type safety
- **Singleton Support**: Performance optimization with connection pooling
- **Health Checking**: Built-in health monitoring for all services
- **FastAPI Integration**: Seamless dependency injection
- **Multiple Patterns**: Decorator, manual, and factory registration methods

## Advanced Usage

### Custom Service Clients

```python
from fast_core.dependencies.client_factory import BaseServiceClient, service_client

@service_client("notification-service", singleton=True)
class NotificationClient(BaseServiceClient):
    async def send_notification(self, user_id: int, message: str):
        client = await self._get_client()
        response = await client.post("/notify", json={
            "user_id": user_id,
            "message": message
        })
        return response.json()

    async def health_check(self):
        return {"service": self.name, "status": "healthy"}
```

### Health Monitoring

```python
from fast_core.dependencies.client_factory import health_check_all_services

@app.get("/health")
async def health_check():
    results = await health_check_all_services()
    all_healthy = all(r.get("status") == "healthy" for r in results.values())
    return {"status": "healthy" if all_healthy else "degraded", "services": results}
```

## Configuration Options

- `name`: Unique service identifier
- `base_url`: Service base URL
- `timeout`: Request timeout in seconds
- `headers`: Default headers for requests
- `singleton`: Use singleton pattern for performance
- `client_class`: Custom client class (defaults to httpx.AsyncClient)
- `client_kwargs`: Additional client configuration

## Best Practices

1. Use singleton pattern for expensive-to-create clients
2. Implement custom health checks for critical services
3. Use environment variables for service URLs and credentials
4. Add comprehensive error handling in custom clients
5. Monitor service health regularly

For complete documentation and examples, see the main Fast Core README.
