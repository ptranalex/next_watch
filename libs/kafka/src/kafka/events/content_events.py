"""Content management events."""

from typing import Any

from pydantic import Field

from kafka.events.base import BaseEvent, EventType


class MovieCreatedEvent(BaseEvent):
    """Event emitted when a new movie is created."""

    event_type: EventType = Field(default=EventType.MOVIE_CREATED, description="Event type")
    movie_id: int = Field(..., description="Unique movie identifier")
    tmdb_id: int = Field(..., description="TMDB movie identifier")
    imdb_id: str | None = Field(default=None, description="IMDB movie identifier")
    title: str = Field(..., description="Movie title")
    original_title: str | None = Field(default=None, description="Original movie title")
    release_date: str | None = Field(default=None, description="Release date (YYYY-MM-DD)")
    genres: list[str] = Field(default_factory=list, description="Movie genres")
    overview: str | None = Field(default=None, description="Movie overview/description")


class MovieUpdatedEvent(BaseEvent):
    """Event emitted when a movie's metadata is updated."""

    event_type: EventType = Field(default=EventType.MOVIE_UPDATED, description="Event type")
    movie_id: int = Field(..., description="Unique movie identifier")
    changed_fields: list[str] = Field(
        default_factory=list, description="List of fields that were updated"
    )
    previous_values: dict[str, Any] = Field(
        default_factory=dict, description="Previous values of changed fields"
    )
    new_values: dict[str, Any] = Field(
        default_factory=dict, description="New values of changed fields"
    )
