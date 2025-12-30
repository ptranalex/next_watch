# Kafka - Shared Kafka Integration Library

A shared library providing Kafka producer, consumer, and event schemas for Next Watch microservices.

## Features

- **Async Kafka Producer**: High-performance async producer with retry logic and OpenTelemetry tracing
- **Base Consumer Class**: Reusable consumer patterns with error handling and DLQ support
- **Event Schemas**: Pydantic models for all event types (user, activity, content, cache, system)
- **Serialization**: JSON and Avro serialization support
- **Monitoring**: Built-in metrics and tracing integration
- **Configuration**: Environment-based configuration with sensible defaults

## Installation

```bash
# Basic installation
pip install -e libs/kafka

# With Avro support
pip install -e "libs/kafka[avro]"

# Development dependencies
pip install -e "libs/kafka[dev]"
```

## Usage

### Producer

```python
from kafka.producer import KafkaEventProducer
from kafka.events import MovieViewedEvent
from kafka.config import KafkaConfig
from datetime import datetime

# Initialize producer
config = KafkaConfig()
producer = KafkaEventProducer(config)
await producer.start()

# Send event
event = MovieViewedEvent(
    user_id=123,
    movie_id=456,
    timestamp=datetime.utcnow()
)
await producer.send_event("user.activity", event, key=str(event.user_id))

# Cleanup
await producer.stop()
```

### Consumer

```python
from kafka.consumer import KafkaEventConsumer
from kafka.events import MovieViewedEvent
from kafka.config import KafkaConfig

class ActivityConsumer(KafkaEventConsumer):
    async def process_message(self, message):
        event = MovieViewedEvent(**message.value)
        print(f"User {event.user_id} viewed movie {event.movie_id}")

# Initialize and run consumer
config = KafkaConfig()
consumer = ActivityConsumer(
    config=config,
    topic="user.activity",
    group_id="recommendation-service"
)
await consumer.start()
await consumer.consume()
```

## Event Schemas

All events are Pydantic models with validation:

- **UserRegisteredEvent**: User registration events
- **UserLoginEvent**: User login events
- **MovieViewedEvent**: Movie viewing events
- **MovieRatedEvent**: Movie rating events
- **WatchlistChangedEvent**: Watchlist modification events
- **MovieCreatedEvent**: New movie creation events
- **MovieUpdatedEvent**: Movie metadata update events
- **CacheInvalidationEvent**: Cache invalidation events
- **RecommendationRequestEvent**: Async recommendation generation

## Configuration

Configuration via environment variables:

```bash
# Kafka broker
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_SECURITY_PROTOCOL=PLAINTEXT

# Producer settings
KAFKA_PRODUCER_ACKS=1
KAFKA_PRODUCER_COMPRESSION_TYPE=snappy
KAFKA_PRODUCER_RETRIES=3

# Consumer settings
KAFKA_CONSUMER_GROUP_ID_PREFIX=next-watch
KAFKA_CONSUMER_AUTO_OFFSET_RESET=earliest

# Schema Registry
KAFKA_SCHEMA_REGISTRY_URL=http://schema-registry:8081

# Feature flags
ENABLE_KAFKA_PRODUCER=true
ENABLE_KAFKA_CONSUMER=true
```

## Topics

The library defines these standard topics:

- `user.events` (8 partitions): Authentication and profile changes
- `user.activity` (16 partitions): Movie interactions
- `content.updates` (4 partitions): Movie metadata changes
- `cache.invalidation` (8 partitions): Cache invalidation
- `recommendation.requests` (8 partitions): Async recommendations
- `ml.training` (4 partitions): Model retraining triggers
- `system.events` (2 partitions): System health events
- `dlq.events` (4 partitions): Dead letter queue

## Development

```bash
# Run tests
cd libs/kafka
hatch run test

# Run tests with coverage
hatch run test-cov

# Lint code
hatch run lint

# Format code
hatch run format
```

## Integration

To integrate this library into a service:

1. Add dependency to service's `pyproject.toml`:

   ```toml
   dependencies = [
       "kafka @ file://../../libs/kafka",
   ]
   ```

2. Initialize producer/consumer in service startup
3. Emit events from business logic
4. Process events in consumer handlers

## License

MIT
