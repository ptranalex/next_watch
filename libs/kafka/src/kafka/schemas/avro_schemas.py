"""Avro schema definitions for all Kafka events.

These schemas enable cross-language event consumption and provide
schema evolution capabilities via Schema Registry.
"""

from typing import Any

***REMOVED*** Namespace for all Next Watch event schemas
NAMESPACE = "com.nextwatch.events"
VERSION = "v1"

***REMOVED*** Base Event Schema (inherited fields in all events)
BASE_EVENT_FIELDS = [
    {"name": "event_id", "type": "string", "doc": "Unique event identifier"},
    {"name": "event_type", "type": "string", "doc": "Type of the event"},
    {
        "name": "timestamp",
        "type": {"type": "long", "logicalType": "timestamp-millis"},
        "doc": "Event timestamp in UTC",
    },
    {
        "name": "service_name",
        "type": ["null", "string"],
        "default": None,
        "doc": "Service that emitted the event",
    },
    {
        "name": "trace_id",
        "type": ["null", "string"],
        "default": None,
        "doc": "Distributed tracing trace ID",
    },
    {
        "name": "span_id",
        "type": ["null", "string"],
        "default": None,
        "doc": "Distributed tracing span ID",
    },
    {
        "name": "metadata",
        "type": {"type": "map", "values": "string"},
        "default": {},
        "doc": "Additional event metadata",
    },
]

***REMOVED*** User Event Schemas
USER_REGISTERED_EVENT_SCHEMA: dict[str, Any] = {
    "type": "record",
    "name": f"UserRegisteredEvent.{VERSION}",
    "namespace": NAMESPACE,
    "doc": "Event emitted when a new user registers",
    "fields": BASE_EVENT_FIELDS
    + [
        {"name": "user_id", "type": "int", "doc": "ID of the registered user"},
        {"name": "email", "type": "string", "doc": "User email address"},
        {"name": "username", "type": "string", "doc": "User chosen username"},
    ],
}

USER_LOGIN_EVENT_SCHEMA: dict[str, Any] = {
    "type": "record",
    "name": f"UserLoginEvent.{VERSION}",
    "namespace": NAMESPACE,
    "doc": "Event emitted when a user logs in",
    "fields": BASE_EVENT_FIELDS
    + [
        {"name": "user_id", "type": "int", "doc": "ID of the logged-in user"},
        {
            "name": "ip_address",
            "type": ["null", "string"],
            "default": None,
            "doc": "Login IP address",
        },
        {
            "name": "user_agent",
            "type": ["null", "string"],
            "default": None,
            "doc": "Browser user agent",
        },
    ],
}

USER_LOGOUT_EVENT_SCHEMA: dict[str, Any] = {
    "type": "record",
    "name": f"UserLogoutEvent.{VERSION}",
    "namespace": NAMESPACE,
    "doc": "Event emitted when a user logs out",
    "fields": BASE_EVENT_FIELDS
    + [
        {"name": "user_id", "type": "int", "doc": "ID of the logged-out user"},
        {
            "name": "session_duration_seconds",
            "type": ["null", "int"],
            "default": None,
            "doc": "Session duration",
        },
    ],
}

***REMOVED*** Activity Event Schemas
MOVIE_VIEWED_EVENT_SCHEMA: dict[str, Any] = {
    "type": "record",
    "name": f"MovieViewedEvent.{VERSION}",
    "namespace": NAMESPACE,
    "doc": "Event emitted when a user views a movie",
    "fields": BASE_EVENT_FIELDS
    + [
        {"name": "user_id", "type": "int", "doc": "ID of the user"},
        {"name": "movie_id", "type": "int", "doc": "ID of the viewed movie"},
        {
            "name": "watch_duration_seconds",
            "type": ["null", "int"],
            "default": None,
            "doc": "Duration watched in seconds",
        },
        {
            "name": "completed",
            "type": "boolean",
            "default": False,
            "doc": "Whether movie was completed",
        },
    ],
}

MOVIE_RATED_EVENT_SCHEMA: dict[str, Any] = {
    "type": "record",
    "name": f"MovieRatedEvent.{VERSION}",
    "namespace": NAMESPACE,
    "doc": "Event emitted when a user rates a movie",
    "fields": BASE_EVENT_FIELDS
    + [
        {"name": "user_id", "type": "int", "doc": "ID of the user"},
        {"name": "movie_id", "type": "int", "doc": "ID of the rated movie"},
        {"name": "rating", "type": "double", "doc": "Rating value (0.0-10.0)"},
        {
            "name": "previous_rating",
            "type": ["null", "double"],
            "default": None,
            "doc": "Previous rating if updating",
        },
    ],
}

WATCHLIST_CHANGED_EVENT_SCHEMA: dict[str, Any] = {
    "type": "record",
    "name": f"WatchlistChangedEvent.{VERSION}",
    "namespace": NAMESPACE,
    "doc": "Event emitted when a user modifies their watchlist",
    "fields": BASE_EVENT_FIELDS
    + [
        {"name": "user_id", "type": "int", "doc": "ID of the user"},
        {"name": "movie_id", "type": "int", "doc": "ID of the movie"},
        {
            "name": "action",
            "type": {"type": "enum", "name": "WatchlistAction", "symbols": ["ADDED", "REMOVED"]},
            "doc": "Action performed on watchlist",
        },
    ],
}

***REMOVED*** Content Event Schemas
MOVIE_CREATED_EVENT_SCHEMA: dict[str, Any] = {
    "type": "record",
    "name": f"MovieCreatedEvent.{VERSION}",
    "namespace": NAMESPACE,
    "doc": "Event emitted when a new movie is added to the catalog",
    "fields": BASE_EVENT_FIELDS
    + [
        {"name": "movie_id", "type": "int", "doc": "ID of the created movie"},
        {"name": "title", "type": "string", "doc": "Movie title"},
        {"name": "release_year", "type": ["null", "int"], "default": None, "doc": "Release year"},
        {"name": "imdb_id", "type": ["null", "string"], "default": None, "doc": "IMDB ID"},
    ],
}

MOVIE_UPDATED_EVENT_SCHEMA: dict[str, Any] = {
    "type": "record",
    "name": f"MovieUpdatedEvent.{VERSION}",
    "namespace": NAMESPACE,
    "doc": "Event emitted when movie metadata is updated",
    "fields": BASE_EVENT_FIELDS
    + [
        {"name": "movie_id", "type": "int", "doc": "ID of the updated movie"},
        {
            "name": "updated_fields",
            "type": {"type": "array", "items": "string"},
            "doc": "List of fields that were updated",
        },
    ],
}

MOVIE_DELETED_EVENT_SCHEMA: dict[str, Any] = {
    "type": "record",
    "name": f"MovieDeletedEvent.{VERSION}",
    "namespace": NAMESPACE,
    "doc": "Event emitted when a movie is removed from the catalog",
    "fields": BASE_EVENT_FIELDS
    + [
        {"name": "movie_id", "type": "int", "doc": "ID of the deleted movie"},
        {"name": "reason", "type": ["null", "string"], "default": None, "doc": "Deletion reason"},
    ],
}

***REMOVED*** Cache Event Schemas
CACHE_INVALIDATION_EVENT_SCHEMA: dict[str, Any] = {
    "type": "record",
    "name": f"CacheInvalidationEvent.{VERSION}",
    "namespace": NAMESPACE,
    "doc": "Event emitted to invalidate cache entries",
    "fields": BASE_EVENT_FIELDS
    + [
        {"name": "cache_key", "type": "string", "doc": "Cache key to invalidate"},
        {
            "name": "cache_pattern",
            "type": ["null", "string"],
            "default": None,
            "doc": "Pattern for bulk invalidation",
        },
        {
            "name": "reason",
            "type": ["null", "string"],
            "default": None,
            "doc": "Invalidation reason",
        },
    ],
}

***REMOVED*** System Event Schemas
RECOMMENDATION_REQUEST_EVENT_SCHEMA: dict[str, Any] = {
    "type": "record",
    "name": f"RecommendationRequestEvent.{VERSION}",
    "namespace": NAMESPACE,
    "doc": "Event to trigger async recommendation generation",
    "fields": BASE_EVENT_FIELDS
    + [
        {"name": "user_id", "type": "int", "doc": "User ID for recommendations"},
        {"name": "strategy", "type": "string", "doc": "Recommendation strategy to use"},
        {"name": "limit", "type": "int", "default": 20, "doc": "Number of recommendations"},
    ],
}

ML_TRAINING_TRIGGER_EVENT_SCHEMA: dict[str, Any] = {
    "type": "record",
    "name": f"MLTrainingTriggerEvent.{VERSION}",
    "namespace": NAMESPACE,
    "doc": "Event to trigger ML model retraining",
    "fields": BASE_EVENT_FIELDS
    + [
        {"name": "model_name", "type": "string", "doc": "Name of the model to retrain"},
        {"name": "trigger_reason", "type": "string", "doc": "Reason for triggering training"},
        {
            "name": "config",
            "type": {"type": "map", "values": "string"},
            "default": {},
            "doc": "Training configuration",
        },
    ],
}

SERVICE_HEALTH_EVENT_SCHEMA: dict[str, Any] = {
    "type": "record",
    "name": f"ServiceHealthEvent.{VERSION}",
    "namespace": NAMESPACE,
    "doc": "Event emitted for service health status changes",
    "fields": BASE_EVENT_FIELDS
    + [
        {"name": "service", "type": "string", "doc": "Service name"},
        {"name": "status", "type": "string", "doc": "Health status (healthy/unhealthy/degraded)"},
        {"name": "message", "type": ["null", "string"], "default": None, "doc": "Status message"},
    ],
}

DLQ_EVENT_SCHEMA: dict[str, Any] = {
    "type": "record",
    "name": f"DLQEvent.{VERSION}",
    "namespace": NAMESPACE,
    "doc": "Event sent to dead letter queue for failed processing",
    "fields": BASE_EVENT_FIELDS
    + [
        {"name": "original_topic", "type": "string", "doc": "Original topic name"},
        {"name": "error_message", "type": "string", "doc": "Error message"},
        {"name": "retry_count", "type": "int", "doc": "Number of retry attempts"},
        {
            "name": "original_payload",
            "type": "string",
            "doc": "Original event payload as JSON string",
        },
    ],
}

***REMOVED*** Dictionary of all schemas for easy lookup
AVRO_SCHEMAS: dict[str, dict[str, Any]] = {
    "user.registered": USER_REGISTERED_EVENT_SCHEMA,
    "user.login": USER_LOGIN_EVENT_SCHEMA,
    "user.logout": USER_LOGOUT_EVENT_SCHEMA,
    "movie.viewed": MOVIE_VIEWED_EVENT_SCHEMA,
    "movie.rated": MOVIE_RATED_EVENT_SCHEMA,
    "watchlist.changed": WATCHLIST_CHANGED_EVENT_SCHEMA,
    "movie.created": MOVIE_CREATED_EVENT_SCHEMA,
    "movie.updated": MOVIE_UPDATED_EVENT_SCHEMA,
    "movie.deleted": MOVIE_DELETED_EVENT_SCHEMA,
    "cache.invalidation": CACHE_INVALIDATION_EVENT_SCHEMA,
    "recommendation.request": RECOMMENDATION_REQUEST_EVENT_SCHEMA,
    "ml.training": ML_TRAINING_TRIGGER_EVENT_SCHEMA,
    "system.health": SERVICE_HEALTH_EVENT_SCHEMA,
    "dlq.event": DLQ_EVENT_SCHEMA,
}
