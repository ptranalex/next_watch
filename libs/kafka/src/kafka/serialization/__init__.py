"""Serialization modules for Kafka messages."""

from kafka.serialization.avro_serializer import AvroDeserializer, AvroSerializer

__all__ = ["AvroSerializer", "AvroDeserializer"]
