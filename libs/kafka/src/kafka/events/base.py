"""Base event schema for all Kafka events."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event type enumeration."""

    ***REMOVED*** User events
    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"

    ***REMOVED*** Activity events
    MOVIE_VIEWED = "movie.viewed"
    MOVIE_RATED = "movie.rated"
    WATCHLIST_CHANGED = "watchlist.changed"

    ***REMOVED*** Content events
    MOVIE_CREATED = "movie.created"
    MOVIE_UPDATED = "movie.updated"

    ***REMOVED*** Cache events
    CACHE_INVALIDATION = "cache.invalidation"

    ***REMOVED*** System events
    RECOMMENDATION_REQUEST = "recommendation.request"
    ML_TRAINING = "ml.training"
    SYSTEM_HEALTH = "system.health"


class BaseEvent(BaseModel):
    """Base event schema for all Kafka events.

    All events should inherit from this base class to ensure consistent
    event structure and metadata.
    """

    event_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique event identifier"
    )
    event_type: EventType = Field(..., description="Type of the event")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Event timestamp in UTC"
    )
    service_name: str | None = Field(
        default=None, description="Name of the service that emitted the event"
    )
    trace_id: str | None = Field(default=None, description="Distributed tracing trace ID")
    span_id: str | None = Field(default=None, description="Distributed tracing span ID")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional event metadata")

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        use_enum_values = True
