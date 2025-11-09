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
    ***REMOVED*** Base
    "BaseEvent",
    "EventType",
    ***REMOVED*** User events
    "UserRegisteredEvent",
    "UserLoginEvent",
    "UserLogoutEvent",
    ***REMOVED*** Activity events
    "MovieViewedEvent",
    "MovieRatedEvent",
    "WatchlistChangedEvent",
    "WatchlistAction",
    ***REMOVED*** Content events
    "MovieCreatedEvent",
    "MovieUpdatedEvent",
    ***REMOVED*** Cache events
    "CacheInvalidationEvent",
    ***REMOVED*** System events
    "RecommendationRequestEvent",
    "MLTrainingEvent",
    "SystemHealthEvent",
]
