"""Service Client Factory Example.

This example demonstrates how to use the Fast Core service client factory
to create and manage service clients in a FastAPI application.
"""

import asyncio
from typing import Dict, Any, List

import httpx
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

from fast_core.dependencies.client_factory import (
    BaseServiceClient,
    ServiceClientConfig,
    register_service,
    register_client_type,
    get_service_client,
    list_services,
    health_check_all_services,
    service_client,
)


***REMOVED*** Example 1: Basic Service Registration
def setup_basic_services():
    """Set up basic service registrations."""
    print("🔧 Setting up basic services...")

    ***REMOVED*** Register basic HTTP services
    register_service(
        name="user-service",
        base_url="https://jsonplaceholder.typicode.com",
        timeout=30,
        headers={"User-Agent": "FastCore-Example"},
        singleton=True,  ***REMOVED*** Use singleton for performance
    )

    register_service(
        name="notification-service",
        base_url="https://api.example.com/notifications",
        timeout=15,
        singleton=False,  ***REMOVED*** Per-request instances
    )

    print("✅ Basic services registered")


***REMOVED*** Example 2: Custom Service Client
class UserServiceClient(BaseServiceClient):
    """Custom client for user service operations."""

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID."""
        client = await self._get_client()
        response = await client.get(f"/users/{user_id}")
        response.raise_for_status()
        return response.json()

    async def get_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get list of users."""
        client = await self._get_client()
        response = await client.get(f"/users?_limit={limit}")
        response.raise_for_status()
        return response.json()

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        client = await self._get_client()
        response = await client.post("/users", json=user_data)
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> Dict[str, Any]:
        """Custom health check for user service."""
        try:
            ***REMOVED*** Check if we can fetch users
            users = await self.get_users(limit=1)
            return {
                "service": self.name,
                "status": "healthy",
                "users_available": len(users) > 0,
                "url": self.base_url,
            }
        except Exception as e:
            return {
                "service": self.name,
                "status": "unhealthy",
                "error": str(e),
                "url": self.base_url,
            }


***REMOVED*** Example 3: Using the @service_client decorator
@service_client("notification-service", singleton=True)
class NotificationServiceClient(BaseServiceClient):
    """Notification service client with decorator registration."""

    async def send_notification(self, user_id: int, message: str) -> Dict[str, Any]:
        """Send notification to user."""
        client = await self._get_client()
        payload = {"user_id": user_id, "message": message, "timestamp": "2024-01-01T00:00:00Z"}

        ***REMOVED*** Simulate API call (this would normally be a real API)
        return {
            "notification_id": f"notif_{user_id}_{hash(message) % 10000}",
            "status": "sent",
            "user_id": user_id,
            "message": message,
        }

    async def health_check(self) -> Dict[str, Any]:
        """Health check for notification service."""
        return {
            "service": self.name,
            "status": "healthy",
            "features": ["push", "email", "sms"],
            "url": self.base_url,
        }


def setup_custom_clients():
    """Set up custom service clients."""
    print("🔧 Setting up custom clients...")

    ***REMOVED*** Register the custom user service client
    register_client_type(
        service_name="user-service",
        client_class=UserServiceClient,
        singleton=True,
    )

    ***REMOVED*** The notification client is automatically registered via decorator
    print("✅ Custom clients registered")


***REMOVED*** Example 4: FastAPI Integration
app = FastAPI(title="Service Client Factory Example")


***REMOVED*** Pydantic models for API
class UserCreate(BaseModel):
    name: str
    email: str
    username: str


class NotificationRequest(BaseModel):
    user_id: int
    message: str


***REMOVED*** Dependency injection
get_user_client = get_service_client("user-service")
get_notification_client = get_service_client("notification-service")


@app.get("/")
async def root():
    """Root endpoint with service information."""
    services = list_services()
    return {
        "message": "Service Client Factory Example",
        "services": services,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for all services."""
    try:
        results = await health_check_all_services()

        ***REMOVED*** Determine overall health
        all_healthy = all(result.get("status") == "healthy" for result in results.values())

        return {
            "status": "healthy" if all_healthy else "degraded",
            "services": results,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


@app.get("/users/{user_id}")
async def get_user(user_id: int, user_client: UserServiceClient = Depends(get_user_client)):
    """Get user by ID."""
    try:
        user = await user_client.get_user(user_id)
        return user
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        raise HTTPException(status_code=500, detail="Service error")


@app.get("/users")
async def get_users(limit: int = 10, user_client: UserServiceClient = Depends(get_user_client)):
    """Get list of users."""
    try:
        users = await user_client.get_users(limit=limit)
        return {"users": users, "count": len(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/users")
async def create_user(
    user_data: UserCreate, user_client: UserServiceClient = Depends(get_user_client)
):
    """Create a new user."""
    try:
        user = await user_client.create_user(user_data.dict())
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/notifications")
async def send_notification(
    notification: NotificationRequest,
    notification_client=Depends(get_notification_client),
):
    """Send notification to user."""
    try:
        result = await notification_client.send_notification(
            notification.user_id, notification.message
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/services")
async def list_registered_services():
    """List all registered services."""
    services = list_services()
    return {"services": services}


***REMOVED*** Example 5: Advanced Usage with Multiple Clients
@app.get("/users/{user_id}/profile")
async def get_user_profile(
    user_id: int,
    user_client: UserServiceClient = Depends(get_user_client),
    notification_client=Depends(get_notification_client),
):
    """Get user profile and send welcome notification."""
    try:
        ***REMOVED*** Get user data
        user = await user_client.get_user(user_id)

        ***REMOVED*** Send welcome notification
        welcome_message = f"Welcome back, {user.get('name', 'User')}!"
        notification_result = await notification_client.send_notification(user_id, welcome_message)

        return {
            "user": user,
            "notification": notification_result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


***REMOVED*** Example 6: Demonstration Functions
async def demonstrate_direct_usage():
    """Demonstrate direct usage of service clients."""
    print("\n🚀 Demonstrating direct service client usage...")

    ***REMOVED*** Create clients directly
    from fast_core.dependencies.client_factory import create_service_client

    user_client = create_service_client("user-service")
    notification_client = create_service_client("notification-service")

    print(f"✅ Created user client: {type(user_client).__name__}")
    print(f"✅ Created notification client: {type(notification_client).__name__}")

    ***REMOVED*** Use the clients
    try:
        ***REMOVED*** Get a user
        user = await user_client.get_user(1)
        print(f"📝 Fetched user: {user.get('name', 'Unknown')}")

        ***REMOVED*** Send notification
        notification = await notification_client.send_notification(1, "Hello from Fast Core!")
        print(f"📨 Sent notification: {notification['notification_id']}")

    except Exception as e:
        print(f"❌ Error during demonstration: {e}")


async def demonstrate_health_checks():
    """Demonstrate health check functionality."""
    print("\n🏥 Demonstrating health checks...")

    try:
        results = await health_check_all_services()

        for service_name, health_result in results.items():
            status = health_result.get("status", "unknown")
            print(f"🔍 {service_name}: {status}")

            if status == "healthy":
                print(f"   ✅ Service is healthy")
            else:
                error = health_result.get("error", "No error details")
                print(f"   ❌ Service issue: {error}")

    except Exception as e:
        print(f"❌ Health check failed: {e}")


def main():
    """Main function to set up and demonstrate the service client factory."""
    print("🎯 Fast Core Service Client Factory Example")
    print("=" * 50)

    ***REMOVED*** Setup services
    setup_basic_services()
    setup_custom_clients()

    ***REMOVED*** Show registered services
    services = list_services()
    print(f"\n📋 Registered services: {len(services)}")
    for name, config in services.items():
        print(f"   • {name}: {config['base_url']} (singleton: {config['singleton']})")

    print("\n🌐 FastAPI app created with endpoints:")
    print("   • GET  /              - Root endpoint")
    print("   • GET  /health        - Health check")
    print("   • GET  /users         - List users")
    print("   • GET  /users/{id}    - Get user")
    print("   • POST /users         - Create user")
    print("   • POST /notifications - Send notification")
    print("   • GET  /services      - List services")

    print("\n🔧 To run the FastAPI server:")
    print("   uvicorn client_factory_example:app --reload")

    ***REMOVED*** Run demonstrations
    asyncio.run(demonstrate_direct_usage())
    asyncio.run(demonstrate_health_checks())

    print("\n✨ Example completed!")


if __name__ == "__main__":
    main()
