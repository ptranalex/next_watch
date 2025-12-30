#!/usr/bin/env python3
"""
Enhanced Error Handling Demo for Fast-Core

This script demonstrates the new intelligent error handling capabilities:
- Semantic error preservation (404 -> ResourceNotFoundException)
- Graceful degradation for non-critical services
- Custom error mapping
- Context-aware logging
- Critical vs optional service handling
"""

import asyncio
import logging
from typing import Any

import httpx
from fast_core.errors import (
    ResourceNotFoundException,
    ValidationException,
    critical_service_handler,
    optional_service_handler,
    service_error_handler,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemoService:
    """Demo service to showcase error handling patterns."""

    def __init__(self) -> None:
        self.client = httpx.AsyncClient()

    @critical_service_handler("user-api", logger)
    async def get_user_profile(self, user_id: int) -> dict[str, Any]:
        """Critical operation - user profile must be available."""
        if user_id <= 0:
            raise ValidationException("Invalid user ID")

        # Simulate API call that might fail
        response = await self.client.get(f"https://jsonplaceholder.typicode.com/users/{user_id}")
        response.raise_for_status()
        return response.json()  # type: ignore

    @optional_service_handler(service_name="recommendation-api", logger=logger, fallback_value=[])
    async def get_recommendations(self, user_id: int) -> list[dict[str, Any]]:
        """Optional operation - gracefully degrades if service unavailable."""
        # Simulate a service that might be down
        response = await self.client.get(f"https://nonexistent-service.com/users/{user_id}/recs")
        response.raise_for_status()
        return response.json()

    @service_error_handler(
        service_name="analytics-api",
        logger=logger,
        error_mapping={
            402: lambda e: ValidationException("Payment required for analytics"),
            "rate_limit": lambda e: ValidationException("Analytics rate limit exceeded"),
        },
    )
    async def track_event(self, event: str) -> dict[str, Any]:
        """Custom error mapping for specific business logic."""
        if event == "payment_failed":
            # Simulate 402 Payment Required
            raise httpx.HTTPStatusError(
                "Payment required",
                request=httpx.Request("POST", "/track"),
                response=httpx.Response(402),
            )
        elif event == "too_many_requests":
            # Simulate rate limiting
            raise Exception("rate_limit: Too many requests")

        return {"status": "tracked", "event": event}

    @service_error_handler(
        service_name="content-api",
        logger=logger,
        preserve_semantics=True,
        graceful_degradation=True,
        fallback_value={"content": "Default content", "source": "fallback"},
    )
    async def get_content(self, content_id: int) -> dict[str, Any]:
        """Semantic preservation with graceful fallback."""
        if content_id == 404:
            # Simulate 404 Not Found
            raise httpx.HTTPStatusError(
                "Not found",
                request=httpx.Request("GET", f"/content/{content_id}"),
                response=httpx.Response(404),
            )
        elif content_id == 500:
            # Simulate server error
            raise Exception("Internal server error")

        return {"content": f"Content {content_id}", "source": "api"}


async def demo_critical_service() -> None:
    """Demo critical service handling."""
    print("\n🔴 Critical Service Demo (user-api)")
    print("=" * 50)

    service = DemoService()

    try:
        # This should work
        user = await service.get_user_profile(1)
        print(f"✅ User retrieved: {user['name']}")
    except Exception as e:
        print(f"❌ Critical service failed: {e}")

    try:
        # This will fail with validation error
        await service.get_user_profile(-1)
    except ValidationException as e:
        print(f"✅ Validation caught: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def demo_optional_service():
    """Demo optional service with graceful degradation."""
    print("\n🟡 Optional Service Demo (recommendation-api)")
    print("=" * 50)

    service = DemoService()

    try:
        # This will fail but gracefully return empty list
        recommendations = await service.get_recommendations(1)
        print(f"✅ Recommendations (graceful degradation): {recommendations}")
        print("   Note: Service failed but returned fallback value instead of crashing")
    except Exception as e:
        print(f"❌ Unexpected error (should not happen): {e}")


async def demo_custom_error_mapping():
    """Demo custom error mapping."""
    print("\n🟠 Custom Error Mapping Demo (analytics-api)")
    print("=" * 50)

    service = DemoService()

    # Test custom 402 mapping
    try:
        await service.track_event("payment_failed")
    except ValidationException as e:
        print(f"✅ Custom 402 mapping: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test custom string pattern mapping
    try:
        await service.track_event("too_many_requests")
    except ValidationException as e:
        print(f"✅ Custom string pattern mapping: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test normal operation
    try:
        result = await service.track_event("user_login")
        print(f"✅ Normal operation: {result}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def demo_semantic_preservation():
    """Demo semantic error preservation."""
    print("\n🔵 Semantic Preservation Demo (content-api)")
    print("=" * 50)

    service = DemoService()

    # Test 404 -> ResourceNotFoundException with graceful fallback
    try:
        content = await service.get_content(404)
        print(f"✅ Graceful degradation for 404: {content}")
        print("   Note: 404 was semantically preserved but gracefully handled")
    except ResourceNotFoundException as e:
        print(f"❌ Should have gracefully degraded: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test server error with graceful fallback
    try:
        content = await service.get_content(500)
        print(f"✅ Graceful degradation for server error: {content}")
        print("   Note: Server error gracefully handled with fallback")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test normal operation
    try:
        content = await service.get_content(123)
        print(f"✅ Normal operation: {content}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def main():
    """Run all demos."""
    print("🚀 Fast-Core Enhanced Error Handling Demo")
    print("=" * 60)

    await demo_critical_service()
    await demo_optional_service()
    await demo_custom_error_mapping()
    await demo_semantic_preservation()

    print("\n🎉 Demo Complete!")
    print("=" * 60)
    print("Key Benefits Demonstrated:")
    print("• Critical services fail fast with proper error types")
    print("• Optional services gracefully degrade to maintain UX")
    print("• Custom error mapping for business-specific logic")
    print("• Semantic error preservation (404 -> ResourceNotFoundException)")
    print("• Enhanced logging with context and function arguments")
    print("• Support for both async and sync functions")


if __name__ == "__main__":
    asyncio.run(main())
