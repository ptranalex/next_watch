"""Kafka event producer with retry logic and OpenTelemetry tracing."""

import asyncio
import json
from typing import Any

import structlog
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError, KafkaTimeoutError
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from kafka.config import KafkaConfig
from kafka.events.base import BaseEvent

logger = structlog.get_logger(__name__)
tracer = trace.get_tracer(__name__)

***REMOVED*** Import Avro dependencies if available
try:
    from kafka.schema_registry import SchemaRegistryClient
    from kafka.schemas.avro_schemas import AVRO_SCHEMAS
    from kafka.serialization.avro_serializer import AvroSerializer

    AVRO_AVAILABLE = True
except ImportError:
    AVRO_AVAILABLE = False
    SchemaRegistryClient = None  ***REMOVED*** type: ignore
    AvroSerializer = None  ***REMOVED*** type: ignore
    AVRO_SCHEMAS = None  ***REMOVED*** type: ignore


class KafkaEventProducer:
    """Async Kafka producer for sending events.

    Features:
    - Automatic retry with exponential backoff
    - OpenTelemetry distributed tracing
    - Dead letter queue for failed messages
    - JSON and Avro serialization support
    - Schema Registry integration (optional)
    - Graceful shutdown handling

    Example:
        >>> config = KafkaConfig()
        >>> producer = KafkaEventProducer(config)
        >>> await producer.start()
        >>>
        >>> event = MovieViewedEvent(user_id=123, movie_id=456)
        >>> await producer.send_event("user.activity", event, key=str(event.user_id))
        >>>
        >>> await producer.stop()
    """

    def __init__(
        self,
        config: KafkaConfig,
        service_name: str | None = None,
        schema_registry: SchemaRegistryClient | None = None,
    ):
        """Initialize Kafka producer.

        Args:
            config: Kafka configuration
            service_name: Name of the service emitting events
            schema_registry: Optional Schema Registry client for Avro serialization
        """
        self.config = config
        self.service_name = service_name
        self._producer: AIOKafkaProducer | None = None
        self._started = False
        self._schema_registry = schema_registry
        self._avro_serializer: AvroSerializer | None = None
        self._schema_ids: dict[str, int] = {}  ***REMOVED*** Cache: event_type -> schema_id
        self.logger = logger.bind(
            component="kafka_producer",
            service=service_name,
            serialization_format=config.serialization_format,
        )

    async def start(self) -> None:
        """Start the Kafka producer."""
        if self._started:
            self.logger.warning("Producer already started")
            return

        if not self.config.enable_producer:
            self.logger.info("Kafka producer disabled by configuration")
            return

        try:
            ***REMOVED*** Initialize Avro serializer if needed
            if self.config.serialization_format == "avro":
                if not AVRO_AVAILABLE:
                    raise RuntimeError(
                        "Avro serialization requested but avro dependencies not installed. "
                        "Install with: pip install kafka[avro]"
                    )

                ***REMOVED*** Create Schema Registry client if not provided
                if not self._schema_registry:
                    if self.config.enable_schema_registry:
                        self._schema_registry = SchemaRegistryClient(self.config)
                        await self._schema_registry.start()
                    else:
                        raise ValueError(
                            "Avro serialization requires Schema Registry to be enabled"
                        )

                self._avro_serializer = AvroSerializer(self._schema_registry)
                self.logger.info("Avro serialization enabled")

            ***REMOVED*** Create producer with appropriate serializer
            if self.config.serialization_format == "avro":
                ***REMOVED*** For Avro, we handle serialization manually in send_event
                self._producer = AIOKafkaProducer(
                    **self.config.producer_config,
                    value_serializer=None,  ***REMOVED*** We'll serialize manually
                    key_serializer=self._serialize_key,
                )
            else:
                ***REMOVED*** For JSON, use existing serializers
                self._producer = AIOKafkaProducer(
                    **self.config.producer_config,
                    value_serializer=self._serialize_value,
                    key_serializer=self._serialize_key,
                )

            await self._producer.start()
            self._started = True
            self.logger.info(
                "Kafka producer started",
                bootstrap_servers=self.config.bootstrap_servers,
                serialization_format=self.config.serialization_format,
            )

            ***REMOVED*** Register schemas if auto-registration is enabled
            if self.config.serialization_format == "avro" and self.config.auto_register_schemas:
                await self._register_all_schemas()

        except Exception as e:
            self.logger.error("Failed to start Kafka producer", error=str(e), exc_info=True)
            raise

    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if not self._started or not self._producer:
            return

        try:
            await self._producer.stop()
            self._started = False
            self.logger.info("Kafka producer stopped")
        except Exception as e:
            self.logger.error("Error stopping Kafka producer", error=str(e), exc_info=True)

    async def send_event(
        self,
        topic: str,
        event: BaseEvent | dict[str, Any],
        key: str | None = None,
        partition: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Send an event to a Kafka topic.

        Args:
            topic: Kafka topic name
            event: Event to send (BaseEvent or dict)
            key: Message key for partitioning (optional)
            partition: Specific partition to send to (optional)
            headers: Additional message headers (optional)

        Raises:
            KafkaError: If message cannot be sent after retries
        """
        if not self._started or not self._producer:
            if self.config.enable_producer:
                self.logger.error("Producer not started, cannot send event")
                raise RuntimeError("Producer not started")
            else:
                self.logger.debug("Producer disabled, skipping event", topic=topic)
                return

        ***REMOVED*** Add service name to event if it's a BaseEvent
        if isinstance(event, BaseEvent):
            if not event.service_name:
                event.service_name = self.service_name

            ***REMOVED*** Add trace context if available
            if self.config.enable_tracing:
                current_span = trace.get_current_span()
                if current_span.is_recording():
                    span_context = current_span.get_span_context()
                    event.trace_id = format(span_context.trace_id, "032x")
                    event.span_id = format(span_context.span_id, "016x")

        ***REMOVED*** Convert event to dict if it's a Pydantic model
        event_data = event.model_dump() if isinstance(event, BaseEvent) else event

        ***REMOVED*** Create trace span
        with tracer.start_as_current_span(
            f"kafka.send.{topic}",
            attributes={
                "messaging.system": "kafka",
                "messaging.destination": topic,
                "messaging.destination_kind": "topic",
            },
        ) as span:
            try:
                ***REMOVED*** Serialize value based on configured format
                if self.config.serialization_format == "avro" and isinstance(event, BaseEvent):
                    serialized_value: bytes | dict[str, Any] = await self._serialize_with_avro(
                        event, topic
                    )
                else:
                    ***REMOVED*** Use JSON serialization (will be handled by producer's serializer)
                    serialized_value = event_data

                await self._send_with_retry(
                    topic=topic,
                    value=serialized_value,
                    key=key,
                    partition=partition,
                    headers=self._prepare_headers(headers),
                )

                span.set_status(Status(StatusCode.OK))
                self.logger.debug(
                    "Event sent successfully",
                    topic=topic,
                    key=key,
                    event_type=event_data.get("event_type"),
                    serialization=self.config.serialization_format,
                )
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)

                ***REMOVED*** Try to send to DLQ
                await self._send_to_dlq(topic, event_data, key, str(e))

                self.logger.error(
                    "Failed to send event after retries",
                    topic=topic,
                    key=key,
                    error=str(e),
                    exc_info=True,
                )
                raise

    async def _send_with_retry(
        self,
        topic: str,
        value: Any,
        key: str | None,
        partition: int | None,
        headers: list | None,
    ) -> None:
        """Send message with retry logic.

        Args:
            topic: Kafka topic
            value: Message value
            key: Message key
            partition: Target partition
            headers: Message headers

        Raises:
            KafkaError: If send fails after all retries
        """
        if not self._producer:
            raise RuntimeError("Producer not started")

        max_retries = self.config.dlq_max_retries
        retry_delay = self.config.producer_retry_backoff_ms / 1000.0

        for attempt in range(max_retries + 1):
            try:
                future = await self._producer.send(
                    topic=topic,
                    value=value,
                    key=key,
                    partition=partition,
                    headers=headers,
                )
                ***REMOVED*** Wait for send to complete
                await future
                return
            except (KafkaTimeoutError, KafkaError) as e:
                if attempt < max_retries:
                    backoff = retry_delay * (2**attempt)
                    self.logger.warning(
                        "Send failed, retrying",
                        topic=topic,
                        attempt=attempt + 1,
                        max_retries=max_retries,
                        backoff_seconds=backoff,
                        error=str(e),
                    )
                    await asyncio.sleep(backoff)
                else:
                    raise

    async def _send_to_dlq(
        self,
        original_topic: str,
        event_data: dict[str, Any],
        key: str | None,
        error_message: str,
    ) -> None:
        """Send failed message to dead letter queue.

        Args:
            original_topic: Original topic where send failed
            event_data: Event data that failed to send
            key: Message key
            error_message: Error message describing the failure
        """
        if not self._producer:
            self.logger.error("Producer not started, cannot send to DLQ")
            return

        try:
            dlq_event = {
                "original_topic": original_topic,
                "original_key": key,
                "error": error_message,
                "event_data": event_data,
                "timestamp": event_data.get("timestamp"),
            }

            ***REMOVED*** Send to DLQ without retry to avoid infinite loop
            await self._producer.send(
                topic=self.config.dlq_topic,
                value=dlq_event,
                key=key,
            )

            self.logger.warning(
                "Event sent to DLQ",
                original_topic=original_topic,
                dlq_topic=self.config.dlq_topic,
            )
        except Exception as e:
            self.logger.error(
                "Failed to send event to DLQ",
                dlq_topic=self.config.dlq_topic,
                error=str(e),
                exc_info=True,
            )

    @staticmethod
    def _serialize_value(value: Any) -> bytes:
        """Serialize message value to JSON bytes.

        Args:
            value: Value to serialize

        Returns:
            Serialized bytes
        """
        return json.dumps(value, default=str).encode("utf-8")

    @staticmethod
    def _serialize_key(key: str | None) -> bytes | None:
        """Serialize message key to bytes.

        Args:
            key: Key to serialize

        Returns:
            Serialized bytes or None
        """
        return key.encode("utf-8") if key else None

    @staticmethod
    def _prepare_headers(headers: dict[str, str] | None) -> list | None:
        """Prepare headers in the format expected by aiokafka.

        Args:
            headers: Headers dictionary

        Returns:
            List of (key, value) tuples or None
        """
        if not headers:
            return None
        return [(k, v.encode("utf-8")) for k, v in headers.items()]

    async def _serialize_with_avro(self, event: BaseEvent, topic: str) -> bytes:
        """Serialize event using Avro format with Schema Registry.

        Args:
            event: Event to serialize
            topic: Topic name

        Returns:
            Serialized Avro bytes with Confluent wire format

        Raises:
            ValueError: If schema not found for event type
        """
        event_type = (
            event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type)
        )

        ***REMOVED*** Get schema ID from cache or register
        if event_type not in self._schema_ids:
            if event_type not in AVRO_SCHEMAS:
                raise ValueError(f"No Avro schema found for event type: {event_type}")

            schema = AVRO_SCHEMAS[event_type]
            subject = f"{topic}-value"

            if not self._schema_registry:
                raise RuntimeError("Schema Registry client not initialized")
            self._schema_ids[event_type] = await self._schema_registry.register_schema(
                subject, schema
            )

            self.logger.debug(
                "Registered schema for event type",
                event_type=event_type,
                subject=subject,
                schema_id=self._schema_ids[event_type],
            )

        schema_id = self._schema_ids[event_type]

        ***REMOVED*** Serialize with Avro using the event and schema ID
        if not self._avro_serializer:
            raise RuntimeError("Avro serializer not initialized")
        return await self._avro_serializer.serialize(event, schema_id)

    async def _register_all_schemas(self) -> None:
        """Register all available event schemas with Schema Registry.

        This is called on startup if auto_register_schemas is enabled.
        """
        if not AVRO_SCHEMAS:
            self.logger.warning("No Avro schemas available to register")
            return

        if not self._schema_registry:
            raise RuntimeError("Schema Registry client not initialized")

        registered_count = 0
        for event_type, schema in AVRO_SCHEMAS.items():
            try:
                ***REMOVED*** Use a generic subject pattern for registration
                subject = f"{event_type}-value"
                schema_id = await self._schema_registry.register_schema(subject, schema)
                self._schema_ids[event_type] = schema_id
                registered_count += 1

                self.logger.debug(
                    "Registered schema",
                    event_type=event_type,
                    subject=subject,
                    schema_id=schema_id,
                )
            except Exception as e:
                self.logger.error(
                    "Failed to register schema",
                    event_type=event_type,
                    error=str(e),
                )

        self.logger.info(
            "Schema registration complete",
            registered_count=registered_count,
            total_schemas=len(AVRO_SCHEMAS),
        )

    async def __aenter__(self) -> "KafkaEventProducer":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.stop()
