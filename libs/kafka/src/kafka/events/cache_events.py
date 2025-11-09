"""Cache management events."""

from pydantic import Field

from kafka.events.base import BaseEvent, EventType


class CacheInvalidationEvent(BaseEvent):
    """Event emitted to invalidate cache entries."""

    event_type: EventType = Field(default=EventType.CACHE_INVALIDATION, description="Event type")
    service: str = Field(..., description="Service name whose cache should be invalidated")
    cache_keys: list[str] = Field(
        default_factory=list, description="Specific cache keys to invalidate (empty for all)"
    )
    pattern: str | None = Field(
        default=None, description="Pattern to match cache keys (e.g., 'movie:*')"
    )
    reason: str | None = Field(default=None, description="Reason for cache invalidation")
