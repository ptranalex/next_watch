"""Shared Kafka integration library for Next Watch microservices."""

from kafka.config import KafkaConfig
from kafka.consumer import KafkaEventConsumer
from kafka.producer import KafkaEventProducer

__version__ = "0.1.0"

__all__ = [
    "KafkaConfig",
    "KafkaEventProducer",
    "KafkaEventConsumer",
]
