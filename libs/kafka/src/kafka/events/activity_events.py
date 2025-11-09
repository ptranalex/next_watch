"""User activity events."""

from enum import Enum

from pydantic import Field

from kafka.events.base import BaseEvent, EventType


class WatchlistAction(str, Enum):
    """Watchlist action type."""

    ADD = "add"
    REMOVE = "remove"


class MovieViewedEvent(BaseEvent):
    """Event emitted when a user views a movie."""

    event_type: EventType = Field(default=EventType.MOVIE_VIEWED, description="Event type")
    user_id: int = Field(..., description="Unique user identifier")
    movie_id: int = Field(..., description="Unique movie identifier")
    duration_seconds: int | None = Field(default=None, description="View duration in seconds")
    completion_percentage: float | None = Field(
        default=None, description="Percentage of movie watched (0-100)"
    )


class MovieRatedEvent(BaseEvent):
    """Event emitted when a user rates a movie."""

    event_type: EventType = Field(default=EventType.MOVIE_RATED, description="Event type")
    user_id: int = Field(..., description="Unique user identifier")
    movie_id: int = Field(..., description="Unique movie identifier")
    rating: float = Field(..., ge=0.0, le=10.0, description="Movie rating (0-10)")
    previous_rating: float | None = Field(
        default=None, description="Previous rating if this is an update"
    )


class WatchlistChangedEvent(BaseEvent):
    """Event emitted when a user's watchlist changes."""

    event_type: EventType = Field(default=EventType.WATCHLIST_CHANGED, description="Event type")
    user_id: int = Field(..., description="Unique user identifier")
    movie_id: int = Field(..., description="Unique movie identifier")
    action: WatchlistAction = Field(..., description="Action performed (add/remove)")
