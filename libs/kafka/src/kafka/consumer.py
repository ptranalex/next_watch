"""Kafka event consumer with error handling and DLQ support."""

import asyncio
import json
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import structlog
from aiokafka import AIOKafkaConsumer
from aiokafka.structs import ConsumerRecord
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from kafka.config import KafkaConfig

logger = structlog.get_logger(__name__)
tracer = trace.get_tracer(__name__)

***REMOVED*** Import Avro dependencies if available
try:
    from kafka.schema_registry import SchemaRegistryClient
    from kafka.serialization.avro_serializer import AvroDeserializer

    AVRO_AVAILABLE = True
except ImportError:
    AVRO_AVAILABLE = False
    SchemaRegistryClient = None  ***REMOVED*** type: ignore
    AvroDeserializer = None  ***REMOVED*** type: ignore


class KafkaEventConsumer(ABC):
    """Base class for Kafka event consumers.

    Features:
    - Automatic offset management
    - Error handling with DLQ support
    - OpenTelemetry distributed tracing
    - Batch processing support
    - Auto-detection of JSON/Avro message formats
    - Graceful shutdown

    Subclasses must implement the process_message method.

    Example:
        >>> class ActivityConsumer(KafkaEventConsumer):
        ...     async def process_message(self, message):
        ...         event = MovieViewedEvent(**message.value)
        ...         print(f"User {event.user_id} viewed {event.movie_id}")
        >>>
        >>> config = KafkaConfig()
        >>> consumer = ActivityConsumer(
        ...     config=config,
        ...     topic="user.activity",
        ...     group_id="recommendation-service"
        ... )
        >>> await consumer.start()
        >>> await consumer.consume()
    """

    def __init__(
        self,
        config: KafkaConfig,
        topic: str | list[str],
        group_id: str,
        enable_auto_commit: bool | None = None,
        message_processor: Callable | None = None,
        schema_registry: SchemaRegistryClient | None = None,
    ):
        """Initialize Kafka consumer.

        Args:
            config: Kafka configuration
            topic: Topic name or list of topics to consume
            group_id: Consumer group ID (will be prefixed with config.consumer_group_id_prefix)
            enable_auto_commit: Override auto-commit setting from config
            message_processor: Optional function to process messages (alternative to subclassing)
            schema_registry: Optional Schema Registry client for Avro deserialization
        """
        self.config = config
        self.topics = [topic] if isinstance(topic, str) else topic
        self.group_id = group_id
        self._enable_auto_commit = (
            enable_auto_commit
            if enable_auto_commit is not None
            else config.consumer_enable_auto_commit
        )
        self._message_processor = message_processor
        self._consumer: AIOKafkaConsumer | None = None
        self._started = False
        self._running = False
        self._shutdown_event = asyncio.Event()
        self._schema_registry = schema_registry
        self._avro_deserializer: AvroDeserializer | None = None
        self.logger = logger.bind(
            component="kafka_consumer",
            group_id=group_id,
            topics=self.topics,
        )

    async def start(self) -> None:
        """Start the Kafka consumer."""
        if self._started:
            self.logger.warning("Consumer already started")
            return

        if not self.config.enable_consumer:
            self.logger.info("Kafka consumer disabled by configuration")
            return

        try:
            ***REMOVED*** Initialize Avro deserializer if Schema Registry is enabled
            if AVRO_AVAILABLE and self.config.enable_schema_registry:
                if not self._schema_registry:
                    self._schema_registry = SchemaRegistryClient(self.config)
                    await self._schema_registry.start()
                self._avro_deserializer = AvroDeserializer(self._schema_registry)
                self.logger.info("Avro deserialization enabled with auto-detection")

            consumer_config = self.config.consumer_config(self.group_id)
            consumer_config["enable_auto_commit"] = self._enable_auto_commit

            ***REMOVED*** Use None deserializer - we'll handle deserialization manually
            ***REMOVED*** to support auto-detection of JSON/Avro formats
            self._consumer = AIOKafkaConsumer(
                *self.topics,
                **consumer_config,
                value_deserializer=None,  ***REMOVED*** Manual deserialization for auto-detection
                key_deserializer=self._deserialize_key,
            )
            await self._consumer.start()
            self._started = True
            self.logger.info(
                "Kafka consumer started",
                bootstrap_servers=self.config.bootstrap_servers,
                avro_enabled=self._avro_deserializer is not None,
            )
        except Exception as e:
            self.logger.error("Failed to start Kafka consumer", error=str(e), exc_info=True)
            raise

    async def stop(self) -> None:
        """Stop the Kafka consumer."""
        if not self._started or not self._consumer:
            return

        self._running = False
        self._shutdown_event.set()

        try:
            await self._consumer.stop()
            self._started = False
            self.logger.info("Kafka consumer stopped")
        except Exception as e:
            self.logger.error("Error stopping Kafka consumer", error=str(e), exc_info=True)

    async def consume(self) -> None:
        """Start consuming messages from Kafka topics.

        This is the main event loop that processes messages until stopped.
        """
        if not self._started or not self._consumer:
            if self.config.enable_consumer:
                self.logger.error("Consumer not started, cannot consume")
                raise RuntimeError("Consumer not started")
            else:
                self.logger.info("Consumer disabled, skipping consumption")
                return

        self._running = True
        self.logger.info("Starting message consumption")

        try:
            while self._running:
                ***REMOVED*** Check for shutdown signal
                if self._shutdown_event.is_set():
                    break

                try:
                    ***REMOVED*** Fetch messages with timeout to allow checking shutdown signal
                    messages = await asyncio.wait_for(
                        self._consumer.getmany(timeout_ms=1000), timeout=2.0
                    )

                    if messages:
                        await self._process_batch(messages)

                except TimeoutError:
                    ***REMOVED*** No messages, continue loop
                    continue
                except Exception as e:
                    self.logger.error("Error in consume loop", error=str(e), exc_info=True)
                    await asyncio.sleep(1)  ***REMOVED*** Brief pause before retrying

        finally:
            self.logger.info("Message consumption stopped")

    async def _process_batch(self, batch: dict[Any, list[ConsumerRecord]]) -> None:
        """Process a batch of messages.

        Args:
            batch: Dictionary of TopicPartition -> List[ConsumerRecord]
        """
        for topic_partition, messages in batch.items():
            for message in messages:
                await self._process_single_message(message)

    async def _process_single_message(self, message: ConsumerRecord) -> None:
        """Process a single message with error handling.

        Args:
            message: Kafka message record
        """
        ***REMOVED*** Deserialize message value with auto-detection
        try:
            deserialized_value = await self._detect_and_deserialize(message.value)
            ***REMOVED*** Create a new message object with deserialized value
            message = ConsumerRecord(
                topic=message.topic,
                partition=message.partition,
                offset=message.offset,
                timestamp=message.timestamp,
                timestamp_type=message.timestamp_type,
                key=message.key,
                value=deserialized_value,
                checksum=message.checksum,
                serialized_key_size=message.serialized_key_size,
                serialized_value_size=message.serialized_value_size,
                headers=message.headers,
            )
        except Exception as e:
            self.logger.error(
                "Failed to deserialize message",
                topic=message.topic,
                partition=message.partition,
                offset=message.offset,
                error=str(e),
                exc_info=True,
            )
            raise

        ***REMOVED*** Extract trace context from message if available
        trace_id = None
        span_id = None
        if message.value and isinstance(message.value, dict):
            trace_id = message.value.get("trace_id")
            span_id = message.value.get("span_id")

        ***REMOVED*** Create trace span
        with tracer.start_as_current_span(
            f"kafka.consume.{message.topic}",
            attributes={
                "messaging.system": "kafka",
                "messaging.destination": message.topic,
                "messaging.destination_kind": "topic",
                "messaging.operation": "receive",
                "messaging.message_id": message.offset,
                "messaging.kafka.partition": message.partition,
            },
        ) as span:
            try:
                ***REMOVED*** Link to producing span if trace context available
                if trace_id and span_id and self.config.enable_tracing:
                    span_context = trace.SpanContext(
                        trace_id=int(trace_id, 16),
                        span_id=int(span_id, 16),
                        is_remote=True,
                        trace_flags=trace.TraceFlags(0x01),
                    )
                    span.add_link(span_context)

                ***REMOVED*** Process message
                if self._message_processor:
                    await self._message_processor(message)
                else:
                    await self.process_message(message)

                span.set_status(Status(StatusCode.OK))

                self.logger.debug(
                    "Message processed successfully",
                    topic=message.topic,
                    partition=message.partition,
                    offset=message.offset,
                )

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)

                self.logger.error(
                    "Error processing message",
                    topic=message.topic,
                    partition=message.partition,
                    offset=message.offset,
                    error=str(e),
                    exc_info=True,
                )

                ***REMOVED*** Send to DLQ
                await self._send_to_dlq(message, str(e))

                ***REMOVED*** Optionally re-raise to stop consumption
                ***REMOVED*** raise

    @abstractmethod
    async def process_message(self, message: ConsumerRecord) -> None:
        """Process a single message.

        This method must be implemented by subclasses to define
        message processing logic.

        Args:
            message: Kafka message record with parsed value

        Raises:
            Exception: Any exception will be caught and logged
        """
        pass

    async def _send_to_dlq(self, message: ConsumerRecord, error_message: str) -> None:
        """Send failed message to dead letter queue.

        Args:
            message: Original Kafka message
            error_message: Error message describing the failure
        """
        try:
            ***REMOVED*** Import producer here to avoid circular dependency
            from kafka.producer import KafkaEventProducer

            ***REMOVED*** Create a temporary producer for DLQ
            async with KafkaEventProducer(self.config) as producer:
                dlq_event = {
                    "original_topic": message.topic,
                    "original_partition": message.partition,
                    "original_offset": message.offset,
                    "original_key": message.key,
                    "original_timestamp": message.timestamp,
                    "error": error_message,
                    "event_data": message.value,
                    "consumer_group": self.group_id,
                }

                await producer.send_event(
                    topic=self.config.dlq_topic,
                    event=dlq_event,
                    key=message.key,
                )

                self.logger.warning(
                    "Message sent to DLQ",
                    original_topic=message.topic,
                    dlq_topic=self.config.dlq_topic,
                )
        except Exception as e:
            self.logger.error(
                "Failed to send message to DLQ",
                dlq_topic=self.config.dlq_topic,
                error=str(e),
                exc_info=True,
            )

    async def _detect_and_deserialize(self, raw_value: bytes | None) -> Any:
        """Detect message format and deserialize appropriately.

        Supports auto-detection of:
        - Avro messages (Confluent wire format with magic byte)
        - JSON messages

        Args:
            raw_value: Raw message bytes

        Returns:
            Deserialized message as dictionary

        Raises:
            Exception: If deserialization fails
        """
        if raw_value is None:
            return None

        ***REMOVED*** Check for Avro magic byte (Confluent wire format)
        if len(raw_value) >= 5 and raw_value[0] == 0x00:
            ***REMOVED*** Likely Avro format
            if self._avro_deserializer:
                try:
                    deserialized = await self._avro_deserializer.deserialize(raw_value)
                    self.logger.debug("Deserialized Avro message")
                    return deserialized
                except Exception as e:
                    self.logger.warning(
                        "Failed to deserialize as Avro, falling back to JSON",
                        error=str(e),
                    )

        ***REMOVED*** Fall back to JSON deserialization
        try:
            deserialized = json.loads(raw_value.decode("utf-8"))
            self.logger.debug("Deserialized JSON message")
            return deserialized
        except Exception as e:
            self.logger.error(
                "Failed to deserialize message as JSON or Avro",
                error=str(e),
                raw_value_preview=str(raw_value[:100]) if len(raw_value) > 100 else str(raw_value),
            )
            ***REMOVED*** Return raw bytes as last resort
            return raw_value

    @staticmethod
    def _deserialize_value(value: bytes | None) -> Any:
        """Deserialize message value from JSON bytes.

        Note: This method is kept for backward compatibility but is not used
        when value_deserializer is set to None in the consumer.

        Args:
            value: Bytes to deserialize

        Returns:
            Deserialized value or None
        """
        if value is None:
            return None
        try:
            return json.loads(value.decode("utf-8"))
        except Exception:
            ***REMOVED*** Return raw bytes if JSON parsing fails
            return value

    @staticmethod
    def _deserialize_key(key: bytes | None) -> str | None:
        """Deserialize message key from bytes.

        Args:
            key: Bytes to deserialize

        Returns:
            Deserialized key string or None
        """
        return key.decode("utf-8") if key else None

    async def __aenter__(self) -> "KafkaEventConsumer":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.stop()
