"""Event schemas for Kafka messages."""

from kafka.events.activity_events import (
    MovieRatedEvent,
    MovieViewedEvent,
    WatchlistAction,
    WatchlistChangedEvent,
)
from kafka.events.base import BaseEvent, EventType
from kafka.events.cache_events import CacheInvalidationEvent
from kafka.events.content_events import MovieCreatedEvent, MovieUpdatedEvent
from kafka.events.system_events import (
    MLTrainingEvent,
    RecommendationRequestEvent,
    SystemHealthEvent,
)
from kafka.events.user_events import UserLoginEvent, UserLogoutEvent, UserRegisteredEvent

__all__ = [
    # Base
    "BaseEvent",
    "EventType",
    # User events
    "UserRegisteredEvent",
    "UserLoginEvent",
    "UserLogoutEvent",
    # Activity events
    "MovieViewedEvent",
    "MovieRatedEvent",
    "WatchlistChangedEvent",
    "WatchlistAction",
    # Content events
    "MovieCreatedEvent",
    "MovieUpdatedEvent",
    # Cache events
    "CacheInvalidationEvent",
    # System events
    "RecommendationRequestEvent",
    "MLTrainingEvent",
    "SystemHealthEvent",
]
