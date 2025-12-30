"""Avro serialization and deserialization for Kafka messages.

Implements the Confluent wire format:
- Magic byte (0x00)
- Schema ID (4 bytes, big-endian)
- Avro-encoded data
"""

import io
import struct
from datetime import UTC
from typing import Any

import fastavro
import structlog

from kafka.events.base import BaseEvent
from kafka.schema_registry import SchemaRegistryClient

logger = structlog.get_logger(__name__)

# Confluent wire format magic byte
MAGIC_BYTE = b"\x00"


class AvroSerializer:
    """Serialize Pydantic events to Avro using Confluent wire format.

    Features:
    - Converts Pydantic models to Avro-compatible dicts
    - Prepends schema ID for Schema Registry integration
    - Uses fastavro for efficient encoding
    - Handles datetime serialization

    Example:
        >>> schema_registry = SchemaRegistryClient(config)
        >>> await schema_registry.start()
        >>>
        >>> serializer = AvroSerializer(schema_registry)
        >>> event = MovieViewedEvent(user_id=123, movie_id=456)
        >>> schema_id = 1
        >>>
        >>> data = await serializer.serialize(event, schema_id)
    """

    def __init__(self, schema_registry: SchemaRegistryClient):
        """Initialize Avro serializer.

        Args:
            schema_registry: Schema Registry client for retrieving schemas
        """
        self.schema_registry = schema_registry
        self.logger = logger.bind(component="avro_serializer")

    async def serialize(self, event: BaseEvent, schema_id: int) -> bytes:
        """Serialize a Pydantic event to Avro bytes.

        Args:
            event: Pydantic event model
            schema_id: Schema ID from Schema Registry

        Returns:
            Avro-encoded bytes with Confluent wire format header

        Raises:
            ValueError: If serialization fails
        """
        try:
            # Get schema from registry
            schema = await self.schema_registry.get_schema(schema_id)

            # Convert Pydantic model to dict
            event_dict = self._pydantic_to_avro_dict(event)

            # Encode with fastavro
            bytes_writer = io.BytesIO()
            fastavro.schemaless_writer(bytes_writer, schema, event_dict)
            avro_bytes = bytes_writer.getvalue()

            # Prepend magic byte and schema ID (Confluent wire format)
            message = MAGIC_BYTE + struct.pack(">I", schema_id) + avro_bytes

            self.logger.debug(
                "Event serialized to Avro",
                event_type=event.event_type,
                schema_id=schema_id,
                size_bytes=len(message),
            )

            return message

        except Exception as e:
            self.logger.error(
                "Failed to serialize event to Avro",
                event_type=getattr(event, "event_type", "unknown"),
                schema_id=schema_id,
                error=str(e),
                exc_info=True,
            )
            raise ValueError(f"Avro serialization failed: {e}") from e

    def _pydantic_to_avro_dict(self, event: BaseEvent) -> dict[str, Any]:
        """Convert Pydantic model to Avro-compatible dictionary.

        Args:
            event: Pydantic event model

        Returns:
            Dictionary compatible with Avro schema
        """
        # Use Pydantic's model_dump with mode='json' for JSON-compatible output
        event_dict = event.model_dump(mode="json")

        # Fastavro expects timestamps as integers (milliseconds since epoch)
        # Pydantic with mode='json' already converts datetime to ISO string,
        # but Avro needs epoch milliseconds for timestamp-millis logical type
        if "timestamp" in event_dict and isinstance(event_dict["timestamp"], str):
            from datetime import datetime

            dt = datetime.fromisoformat(event_dict["timestamp"].replace("Z", "+00:00"))
            event_dict["timestamp"] = int(dt.timestamp() * 1000)

        return event_dict


class AvroDeserializer:
    """Deserialize Avro messages to dictionaries.

    Features:
    - Extracts schema ID from Confluent wire format
    - Fetches schema from Registry
    - Uses fastavro for efficient decoding
    - Caches schemas for performance

    Example:
        >>> schema_registry = SchemaRegistryClient(config)
        >>> await schema_registry.start()
        >>>
        >>> deserializer = AvroDeserializer(schema_registry)
        >>> message_bytes = b"\\x00\\x00\\x00\\x00\\x01..."  # Avro message
        >>>
        >>> event_dict = await deserializer.deserialize(message_bytes)
    """

    def __init__(self, schema_registry: SchemaRegistryClient):
        """Initialize Avro deserializer.

        Args:
            schema_registry: Schema Registry client for retrieving schemas
        """
        self.schema_registry = schema_registry
        self._reader_cache: dict[int, Any] = {}
        self.logger = logger.bind(component="avro_deserializer")

    async def deserialize(self, data: bytes) -> dict[str, Any]:
        """Deserialize Avro bytes to dictionary.

        Args:
            data: Avro-encoded bytes with Confluent wire format header

        Returns:
            Deserialized event as dictionary

        Raises:
            ValueError: If deserialization fails
        """
        if len(data) < 5:
            raise ValueError("Message too short for Confluent wire format")

        # Extract magic byte and schema ID
        magic = data[0:1]
        if magic != MAGIC_BYTE:
            raise ValueError(f"Invalid magic byte: {magic!r}, expected {MAGIC_BYTE!r}")

        schema_id = struct.unpack(">I", data[1:5])[0]
        avro_data = data[5:]

        try:
            # Get schema from registry (cached)
            schema = await self.schema_registry.get_schema(schema_id)

            # Deserialize with fastavro
            bytes_reader = io.BytesIO(avro_data)
            event_dict = fastavro.schemaless_reader(bytes_reader, schema)

            # Convert timestamp back to datetime if present
            if "timestamp" in event_dict and isinstance(event_dict["timestamp"], int):
                from datetime import datetime

                event_dict["timestamp"] = datetime.fromtimestamp(
                    event_dict["timestamp"] / 1000, tz=UTC
                ).isoformat()

            self.logger.debug(
                "Event deserialized from Avro",
                schema_id=schema_id,
                event_type=event_dict.get("event_type"),
            )

            return event_dict

        except Exception as e:
            self.logger.error(
                "Failed to deserialize Avro message",
                schema_id=schema_id,
                error=str(e),
                exc_info=True,
            )
            raise ValueError(f"Avro deserialization failed: {e}") from e

    def can_deserialize(self, data: bytes) -> bool:
        """Check if data is Avro-encoded with Confluent wire format.

        Args:
            data: Raw message bytes

        Returns:
            True if data starts with Confluent magic byte
        """
        return len(data) >= 5 and data[0:1] == MAGIC_BYTE
