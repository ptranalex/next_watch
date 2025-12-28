"""Kafka consumer for content update events in Search API."""

import asyncio
from typing import Any

import structlog
from aiokafka.structs import ConsumerRecord
from kafka import KafkaConfig, KafkaEventConsumer
from kafka.events import MovieCreatedEvent, MovieUpdatedEvent

logger = structlog.get_logger(__name__)


class ContentConsumer(KafkaEventConsumer):
    """Consumer for processing content update events.

    This consumer listens to content.updates topic and updates:
    - Redis search indices
    - Autocomplete suggestions
    - Search rankings
    """

    def __init__(self, config: KafkaConfig):
        """Initialize content consumer."""
        super().__init__(
            config=config,
            topic="content.updates",
            group_id="search-service",
        )
        self.logger = logger.bind(component="content_consumer")

    async def process_message(self, message: ConsumerRecord) -> None:
        """Process a single content event."""
        event_type: str | None = None
        try:
            raw_value = message.value
            if not isinstance(raw_value, dict):
                self.logger.warning(
                    "Invalid content event payload; expected dict",
                    payload_type=type(raw_value).__name__,
                )
                return

            event_type = raw_value.get("event_type")

            if event_type == "movie.created":
                await self._handle_movie_created(raw_value)
            elif event_type == "movie.updated":
                await self._handle_movie_updated(raw_value)
            else:
                self.logger.warning("Unknown event type", event_type=event_type)

        except Exception as e:
            self.logger.error(
                "Error processing content event",
                error=str(e),
                event_type=event_type,
                exc_info=True,
            )
            raise

    async def _handle_movie_created(self, event_data: dict[str, Any]) -> None:
        """Handle movie created event."""
        event = MovieCreatedEvent(**event_data)

        self.logger.info(
            "Processing movie created event",
            movie_id=event.movie_id,
            title=event.title,
        )

        ***REMOVED*** TODO: Implement logic to:
        ***REMOVED*** 1. Add movie to Redis search index
        ***REMOVED*** 2. Update autocomplete suggestions with new title
        ***REMOVED*** 3. Index genres, actors, etc. for search
        ***REMOVED*** 4. Initialize search popularity metrics

    async def _handle_movie_updated(self, event_data: dict[str, Any]) -> None:
        """Handle movie updated event."""
        event = MovieUpdatedEvent(**event_data)

        self.logger.info(
            "Processing movie updated event",
            movie_id=event.movie_id,
            changed_fields=event.changed_fields,
        )

        ***REMOVED*** TODO: Implement logic to:
        ***REMOVED*** 1. Update search index with changed fields
        ***REMOVED*** 2. Refresh autocomplete if title changed
        ***REMOVED*** 3. Update search rankings if popularity changed


async def start_content_consumer() -> None:
    """Start the content consumer."""
    config = KafkaConfig()
    consumer = ContentConsumer(config)

    try:
        await consumer.start()
        logger.info("Content consumer started")
        await consumer.consume()
    except KeyboardInterrupt:
        logger.info("Content consumer interrupted")
    finally:
        await consumer.stop()
        logger.info("Content consumer stopped")


if __name__ == "__main__":
    asyncio.run(start_content_consumer())
