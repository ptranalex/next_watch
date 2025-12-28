"""Kafka event streaming service for Backend API."""

from typing import Optional

import structlog
from kafka import KafkaConfig, KafkaEventProducer
from kafka.events import (
    MovieRatedEvent,
    MovieViewedEvent,
    WatchlistAction,
    WatchlistChangedEvent,
)

logger = structlog.get_logger(__name__)


class BackendKafkaService:
    """Service for emitting Kafka events from Backend API.

    This service provides convenient methods for emitting domain events
    from backend operations to Kafka topics.
    """

    _instance: Optional["BackendKafkaService"] = None
    _producer: KafkaEventProducer | None = None

    def __init__(self, config: KafkaConfig | None = None):
        """Initialize Kafka service.

        Args:
            config: Kafka configuration (will be created from env if not provided)
        """
        self.config = config or KafkaConfig()
        self.logger = logger.bind(component="backend_kafka_service")

    @classmethod
    def get_instance(cls, config: KafkaConfig | None = None) -> "BackendKafkaService":
        """Get singleton instance of Kafka service.

        Args:
            config: Kafka configuration (only used on first call)

        Returns:
            Singleton instance
        """
        if cls._instance is None:
            cls._instance = cls(config)
        return cls._instance

    async def start(self) -> None:
        """Start the Kafka producer."""
        if self._producer is not None:
            self.logger.warning("Kafka producer already started")
            return

        try:
            self._producer = KafkaEventProducer(config=self.config, service_name="backend-api")
            await self._producer.start()
            self.logger.info("Kafka producer started")
        except Exception as e:
            self.logger.error("Failed to start Kafka producer", error=str(e), exc_info=True)
            ***REMOVED*** Don't raise - service should continue even if Kafka is unavailable

    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if self._producer is None:
            return

        try:
            await self._producer.stop()
            self._producer = None
            self.logger.info("Kafka producer stopped")
        except Exception as e:
            self.logger.error("Error stopping Kafka producer", error=str(e), exc_info=True)

    async def emit_movie_viewed(
        self,
        user_id: int,
        movie_id: int,
        duration_seconds: int | None = None,
        completion_percentage: float | None = None,
    ) -> None:
        """Emit a movie viewed event.

        Args:
            user_id: User who viewed the movie
            movie_id: Movie that was viewed
            duration_seconds: How long the movie was viewed
            completion_percentage: Percentage of movie watched
        """
        if not self._producer or not self.config.enable_producer:
            self.logger.debug("Producer not available, skipping event emission")
            return

        try:
            event = MovieViewedEvent(
                user_id=user_id,
                movie_id=movie_id,
                duration_seconds=duration_seconds,
                completion_percentage=completion_percentage,
            )

            await self._producer.send_event(
                topic="user.activity",
                event=event,
                key=str(user_id),  ***REMOVED*** Partition by user_id
            )

            self.logger.debug(
                "Movie viewed event emitted",
                user_id=user_id,
                movie_id=movie_id,
            )
        except Exception as e:
            self.logger.error(
                "Failed to emit movie viewed event",
                user_id=user_id,
                movie_id=movie_id,
                error=str(e),
                exc_info=True,
            )

    async def emit_movie_rated(
        self,
        user_id: int,
        movie_id: int,
        rating: float,
        previous_rating: float | None = None,
    ) -> None:
        """Emit a movie rated event.

        Args:
            user_id: User who rated the movie
            movie_id: Movie that was rated
            rating: New rating value
            previous_rating: Previous rating if this is an update
        """
        if not self._producer or not self.config.enable_producer:
            self.logger.debug("Producer not available, skipping event emission")
            return

        try:
            event = MovieRatedEvent(
                user_id=user_id,
                movie_id=movie_id,
                rating=rating,
                previous_rating=previous_rating,
            )

            await self._producer.send_event(
                topic="user.activity",
                event=event,
                key=str(user_id),
            )

            self.logger.debug(
                "Movie rated event emitted",
                user_id=user_id,
                movie_id=movie_id,
                rating=rating,
            )
        except Exception as e:
            self.logger.error(
                "Failed to emit movie rated event",
                user_id=user_id,
                movie_id=movie_id,
                error=str(e),
                exc_info=True,
            )

    async def emit_watchlist_changed(
        self,
        user_id: int,
        movie_id: int,
        action: WatchlistAction,
    ) -> None:
        """Emit a watchlist changed event.

        Args:
            user_id: User whose watchlist changed
            movie_id: Movie that was added/removed
            action: Action performed (add/remove)
        """
        if not self._producer or not self.config.enable_producer:
            self.logger.debug("Producer not available, skipping event emission")
            return

        try:
            event = WatchlistChangedEvent(
                user_id=user_id,
                movie_id=movie_id,
                action=action,
            )

            await self._producer.send_event(
                topic="user.activity",
                event=event,
                key=str(user_id),
            )

            self.logger.debug(
                "Watchlist changed event emitted",
                user_id=user_id,
                movie_id=movie_id,
                action=action.value,
            )
        except Exception as e:
            self.logger.error(
                "Failed to emit watchlist changed event",
                user_id=user_id,
                movie_id=movie_id,
                error=str(e),
                exc_info=True,
            )


***REMOVED*** Global Kafka service instance
_kafka_service: BackendKafkaService | None = None


async def get_kafka_service() -> BackendKafkaService:
    """Get the global Kafka service instance.

    Returns:
        Kafka service instance
    """
    global _kafka_service
    if _kafka_service is None:
        _kafka_service = BackendKafkaService.get_instance()
        await _kafka_service.start()
    return _kafka_service


async def stop_kafka_service() -> None:
    """Stop the global Kafka service."""
    global _kafka_service
    if _kafka_service is not None:
        await _kafka_service.stop()
        _kafka_service = None
