"""System and internal events."""

from typing import Any

from pydantic import Field

from kafka.events.base import BaseEvent, EventType


class RecommendationRequestEvent(BaseEvent):
    """Event emitted to request async recommendation generation."""

    event_type: EventType = Field(
        default=EventType.RECOMMENDATION_REQUEST, description="Event type"
    )
    user_id: int = Field(..., description="User identifier")
    context: dict[str, Any] = Field(
        default_factory=dict, description="Recommendation context (filters, preferences, etc.)"
    )
    count: int = Field(default=10, description="Number of recommendations requested")
    callback_url: str | None = Field(default=None, description="URL to POST results to when ready")


class MLTrainingEvent(BaseEvent):
    """Event emitted to trigger ML model training."""

    event_type: EventType = Field(default=EventType.ML_TRAINING, description="Event type")
    model_type: str = Field(
        ..., description="Type of model to train (embeddings, recommendations, etc.)"
    )
    training_data_ids: list[int] = Field(
        default_factory=list, description="IDs of data to use for training"
    )
    config: dict[str, Any] = Field(
        default_factory=dict, description="Training configuration parameters"
    )


class SystemHealthEvent(BaseEvent):
    """Event emitted for system health status changes."""

    event_type: EventType = Field(default=EventType.SYSTEM_HEALTH, description="Event type")
    service: str = Field(..., description="Service name")
    status: str = Field(..., description="Health status (healthy, degraded, unhealthy)")
    details: dict[str, Any] = Field(default_factory=dict, description="Health check details")
