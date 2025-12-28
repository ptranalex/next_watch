"""Kafka consumer for user activity events in Recommendation API."""

import asyncio
from typing import Any

import structlog
from aiokafka.structs import ConsumerRecord
from kafka import KafkaConfig, KafkaEventConsumer
from kafka.events import MovieRatedEvent, MovieViewedEvent, WatchlistChangedEvent

logger = structlog.get_logger(__name__)


class ActivityConsumer(KafkaEventConsumer):
    """Consumer for processing user activity events.

    This consumer listens to user.activity topic and updates:
    - User preference vectors
    - Cached recommendations (invalidation)
    - Qdrant embeddings based on interactions
    """

    def __init__(self, config: KafkaConfig):
        """Initialize activity consumer.

        Args:
            config: Kafka configuration
        """
        super().__init__(
            config=config,
            topic="user.activity",
            group_id="recommendation-service",
        )
        self.logger = logger.bind(component="activity_consumer")

    async def process_message(self, message: ConsumerRecord) -> None:
        """Process a single activity event.

        Args:
            message: Kafka message containing activity event
        """
        event_type: str | None = None
        try:
            raw_value = message.value
            if not isinstance(raw_value, dict):
                self.logger.warning(
                    "Invalid activity event payload; expected dict",
                    payload_type=type(raw_value).__name__,
                )
                return

            event_type = raw_value.get("event_type")

            if event_type == "movie.viewed":
                await self._handle_movie_viewed(raw_value)
            elif event_type == "movie.rated":
                await self._handle_movie_rated(raw_value)
            elif event_type == "watchlist.changed":
                await self._handle_watchlist_changed(raw_value)
            else:
                self.logger.warning("Unknown event type", event_type=event_type)

        except Exception as e:
            self.logger.error(
                "Error processing activity event",
                error=str(e),
                event_type=event_type,
                exc_info=True,
            )
            raise

    async def _handle_movie_viewed(self, event_data: dict[str, Any]) -> None:
        """Handle movie viewed event.

        Args:
            event_data: Event data dictionary
        """
        event = MovieViewedEvent(**event_data)

        self.logger.info(
            "Processing movie viewed event",
            user_id=event.user_id,
            movie_id=event.movie_id,
        )

        ***REMOVED*** TODO: Implement logic to:
        ***REMOVED*** 1. Update user's view history
        ***REMOVED*** 2. Invalidate cached recommendations for this user
        ***REMOVED*** 3. Update collaborative filtering data
        ***REMOVED*** 4. Trigger recommendation cache warming for active user

        ***REMOVED*** Example:
        ***REMOVED*** await self.recommendation_service.invalidate_user_cache(event.user_id)
        ***REMOVED*** await self.recommendation_service.update_user_preferences(event.user_id)

    async def _handle_movie_rated(self, event_data: dict[str, Any]) -> None:
        """Handle movie rated event.

        Args:
            event_data: Event data dictionary
        """
        event = MovieRatedEvent(**event_data)

        self.logger.info(
            "Processing movie rated event",
            user_id=event.user_id,
            movie_id=event.movie_id,
            rating=event.rating,
        )

        ***REMOVED*** TODO: Implement logic to:
        ***REMOVED*** 1. Update user preference vector based on rating
        ***REMOVED*** 2. Invalidate cached recommendations
        ***REMOVED*** 3. Update collaborative filtering matrix
        ***REMOVED*** 4. Potentially trigger model retraining if significant rating

    async def _handle_watchlist_changed(self, event_data: dict[str, Any]) -> None:
        """Handle watchlist changed event.

        Args:
            event_data: Event data dictionary
        """
        event = WatchlistChangedEvent(**event_data)

        self.logger.info(
            "Processing watchlist changed event",
            user_id=event.user_id,
            movie_id=event.movie_id,
            action=event.action,
        )

        ***REMOVED*** TODO: Implement logic to:
        ***REMOVED*** 1. Update user's watchlist preferences
        ***REMOVED*** 2. Adjust recommendation weights
        ***REMOVED*** 3. Invalidate relevant caches


async def start_activity_consumer() -> None:
    """Start the activity consumer."""
    config = KafkaConfig()
    consumer = ActivityConsumer(config)

    try:
        await consumer.start()
        logger.info("Activity consumer started")
        await consumer.consume()
    except KeyboardInterrupt:
        logger.info("Activity consumer interrupted")
    finally:
        await consumer.stop()
        logger.info("Activity consumer stopped")


if __name__ == "__main__":
    asyncio.run(start_activity_consumer())
