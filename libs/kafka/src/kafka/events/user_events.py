"""User-related events."""

from pydantic import Field

from kafka.events.base import BaseEvent, EventType


class UserRegisteredEvent(BaseEvent):
    """Event emitted when a new user registers."""

    event_type: EventType = Field(default=EventType.USER_REGISTERED, description="Event type")
    user_id: int = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    username: str | None = Field(default=None, description="User username (optional)")


class UserLoginEvent(BaseEvent):
    """Event emitted when a user logs in."""

    event_type: EventType = Field(default=EventType.USER_LOGIN, description="Event type")
    user_id: int = Field(..., description="Unique user identifier")
    ip_address: str | None = Field(default=None, description="User IP address")
    user_agent: str | None = Field(default=None, description="User agent string")


class UserLogoutEvent(BaseEvent):
    """Event emitted when a user logs out."""

    event_type: EventType = Field(default=EventType.USER_LOGOUT, description="Event type")
    user_id: int = Field(..., description="Unique user identifier")
