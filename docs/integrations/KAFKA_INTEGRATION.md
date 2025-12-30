# Kafka Integration for Next Watch

## Overview

This document describes the Apache Kafka integration for the Next Watch microservices platform. Kafka provides event streaming capabilities that enable:

- Real-time user activity tracking
- Async task processing across services
- Cache invalidation and data synchronization
- ML model retraining triggers
- Audit logging and analytics

## Architecture

### Event Flow

```
Producer Services          Kafka Topics              Consumer Services
┌─────────────────┐       ┌──────────────┐          ┌──────────────────┐
│  Backend API    │──────►│user.activity │─────────►│ Recommendation  │
│  (User Actions) │       │(16 partitions)│          │ ML API          │
└─────────────────┘       └──────────────┘          └──────────────────┘

┌─────────────────┐       ┌──────────────┐          ┌──────────────────┐
│  Auth API       │──────►│ user.events  │─────────►│ Analytics       │
│  (Auth Events)  │       │ (8 partitions)│          │ Audit Log       │
└─────────────────┘       └──────────────┘          └──────────────────┘

┌─────────────────┐       ┌──────────────┐          ┌──────────────────┐
│ Data Importer   │──────►│content.updates│────────►│  Search API     │
│ (Content Updates)│       │ (4 partitions)│          │  Cache Services │
└─────────────────┘       └──────────────┘          └──────────────────┘
```

## Infrastructure Components

### 1. Kafka Cluster

- **Broker**: Single broker for development/staging, clustered for production
- **Zookeeper**: Cluster coordination
- **Schema Registry**: Event schema management and validation
- **Kafka UI**: Web-based management interface

### 2. Topics

| Topic                     | Partitions | Retention | Purpose                                             |
| ------------------------- | ---------- | --------- | --------------------------------------------------- |
| `user.events`             | 8          | 7 days    | Authentication events (login, logout, registration) |
| `user.activity`           | 16         | 7 days    | Movie interactions (views, ratings, watchlist)      |
| `content.updates`         | 4          | 30 days   | Movie metadata changes                              |
| `cache.invalidation`      | 8          | 1 day     | Cache invalidation signals                          |
| `recommendation.requests` | 8          | 3 days    | Async recommendation generation                     |
| `ml.training`             | 4          | 7 days    | Model retraining triggers                           |
| `system.events`           | 2          | 7 days    | System health and status                            |
| `dlq.events`              | 4          | 30 days   | Dead letter queue for failed events                 |

## Shared Library (libs/kafka)

The `kafka` library provides:

- **KafkaEventProducer**: Async producer with retry and tracing
- **KafkaEventConsumer**: Base consumer class with error handling
- **Event Schemas**: Pydantic models for all event types
- **Configuration**: Environment-based Kafka settings

### Installation

```bash
pip install -e libs/kafka
```

### Configuration

Environment variables:

```bash
# Required
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# Optional
KAFKA_SECURITY_PROTOCOL=PLAINTEXT
KAFKA_PRODUCER_ACKS=1
KAFKA_PRODUCER_COMPRESSION_TYPE=snappy
KAFKA_CONSUMER_GROUP_ID_PREFIX=next-watch
ENABLE_KAFKA_PRODUCER=true
ENABLE_KAFKA_CONSUMER=true
```

## Producer Integration

### Example: Backend API

```python
from kafka import KafkaEventProducer, KafkaConfig
from kafka.events import MovieViewedEvent

# Initialize producer (typically in app startup)
config = KafkaConfig()
producer = KafkaEventProducer(config, service_name="backend-api")
await producer.start()

# Emit event after database operation
event = MovieViewedEvent(
    user_id=user_id,
    movie_id=movie_id,
    timestamp=datetime.utcnow()
)
await producer.send_event(
    topic="user.activity",
    event=event,
    key=str(user_id)  # Partition by user
)
```

### Integration Points

**Backend API**:

- User interactions (watchlist, favorites, ratings)
- Movie operations (CRUD)
- Example: `apps/backend-api/src/backend_api/routes/v1/user_collections.py`

**Auth API**:

- User registration
- Login/logout events
- Example: `apps/auth-api/src/auth_api/services/kafka_service.py`

**Data Importer**:

- New movie imports
- Metadata updates
- Batch event emission

## Consumer Integration

### Example: Recommendation API

```python
from kafka import KafkaEventConsumer, KafkaConfig
from kafka.events import MovieViewedEvent

class ActivityConsumer(KafkaEventConsumer):
    async def process_message(self, message):
        event_type = message.value.get("event_type")

        if event_type == "movie.viewed":
            event = MovieViewedEvent(**message.value)
            await self._update_user_preferences(event)

# Start consumer
config = KafkaConfig()
consumer = ActivityConsumer(
    config=config,
    topic="user.activity",
    group_id="recommendation-service"
)
await consumer.start()
await consumer.consume()
```

### Consumer Services

**Recommendation API**:

- Topic: `user.activity`
- Actions: Update preferences, invalidate cache, trigger warming
- File: `apps/recommendation-api/src/recommendation_api/consumers/activity_consumer.py`

**Search API**:

- Topic: `content.updates`
- Actions: Update search indices, refresh autocomplete
- File: `apps/search-api/src/search_api/consumers/content_consumer.py`

**BFF API**:

- Topic: `cache.invalidation`
- Actions: Invalidate cache keys, trigger warming
- File: `apps/bff-api/src/bff_api/consumers/cache_consumer.py`

**ML API**:

- Topic: `ml.training`
- Actions: Aggregate data, trigger model retraining

## Event Schemas

All events inherit from `BaseEvent`:

```python
class BaseEvent(BaseModel):
    event_id: str          # UUID
    event_type: EventType  # Enum of event types
    timestamp: datetime    # UTC timestamp
    service_name: str      # Producing service
    trace_id: str          # Distributed tracing
    metadata: Dict         # Additional data
```

### User Events

```python
UserRegisteredEvent(user_id, email, username)
UserLoginEvent(user_id, ip_address, user_agent)
UserLogoutEvent(user_id)
```

### Activity Events

```python
MovieViewedEvent(user_id, movie_id, duration_seconds)
MovieRatedEvent(user_id, movie_id, rating, previous_rating)
WatchlistChangedEvent(user_id, movie_id, action)  # action: ADD/REMOVE
```

### Content Events

```python
MovieCreatedEvent(movie_id, tmdb_id, title, genres, overview)
MovieUpdatedEvent(movie_id, changed_fields, previous_values, new_values)
```

## Monitoring

### Metrics

Prometheus metrics exposed at `/metrics`:

- `kafka_producer_send_total`: Total messages sent
- `kafka_producer_send_errors_total`: Send errors
- `kafka_consumer_lag`: Consumer lag by topic
- `kafka_consumer_messages_processed_total`: Processed messages

### Grafana Dashboards

1. **Kafka Overview**: Cluster health, throughput, latency
2. **Consumer Lag**: Per-topic consumer lag monitoring
3. **Event Flow**: End-to-end event processing metrics

### Alerts

Configured in `infra/monitoring/prometheus/kafka-alerts.yml`:

- Consumer lag > 10000 messages (WARNING)
- Consumer lag > 50000 messages (CRITICAL)
- Kafka broker down
- No active controller
- Offline partitions
- High memory usage

## CLI Tools

### Kafka Management

```bash
# List topics
python -m kafka.cli_tools list-topics

# Create topic
python -m kafka.cli_tools create-topic --name test.events --partitions 8

# Describe topic
python -m kafka.cli_tools describe-topic --name user.activity

# Check consumer lag
python -m kafka.cli_tools consumer-lag --group recommendation-service

# Send test event
python -m kafka.cli_tools send-event --topic user.activity --data '{"user_id": 123}'

# Consume events
python -m kafka.cli_tools consume --topic user.activity --count 10
```

## Deployment

### Local Development

```bash
# Start Kafka services
docker compose -f infra/compose/prod.yml up -d zookeeper kafka schema-registry kafka-ui

# Initialize topics
bash infra/kafka/init-topics.sh

# Access Kafka UI
open http://localhost:8080
```

### Production

Kafka services are defined in `infra/compose/prod.yml` and started with other services:

```bash
docker compose -f infra/compose/prod.yml up -d
```

## Feature Flags

Control Kafka integration with environment variables:

```bash
# Disable producer (read-only mode)
ENABLE_KAFKA_PRODUCER=false

# Disable consumer (no event processing)
ENABLE_KAFKA_CONSUMER=false
```

This allows gradual rollout and safe rollback.

## Error Handling

### Dead Letter Queue

Failed events are automatically sent to `dlq.events` topic after 3 retry attempts. Monitor DLQ for:

- Schema validation errors
- Processing exceptions
- Timeout errors

### Retry Logic

- Producer: Exponential backoff with 3 retries
- Consumer: Configurable retry with DLQ fallback
- Timeout: 30s default for operations

## Best Practices

1. **Partitioning**: Use consistent keys (user_id, movie_id) for ordering
2. **Idempotency**: Design consumers to handle duplicate messages
3. **Monitoring**: Watch consumer lag closely
4. **Schema Evolution**: Use Schema Registry for compatibility
5. **Error Handling**: Never fail requests due to Kafka errors
6. **Testing**: Use test topics for development

## Troubleshooting

### Consumer Lag Growing

```bash
# Check consumer status
python -m kafka.cli_tools consumer-lag --group <group-id>

# Scale consumers (add more instances)
# or increase batch size in consumer config
```

### Events Not Processing

1. Check consumer is running: `docker ps | grep <service>`
2. Check consumer logs: `docker logs <service>`
3. Verify topic exists: `python -m kafka.cli_tools list-topics`
4. Check DLQ for failed events

### Kafka Broker Issues

1. Check broker health: `docker logs kafka`
2. Verify Zookeeper: `docker logs zookeeper`
3. Check disk space: `df -h`
4. Review Grafana alerts

## Migration Strategy

1. **Phase 1**: Deploy Kafka infrastructure
2. **Phase 2**: Enable producers (events flowing)
3. **Phase 3**: Deploy consumers (event processing)
4. **Phase 4**: Monitor and optimize
5. **Phase 5**: Full production rollout

## Performance Tuning

### Producer

```python
# Increase batch size for throughput
KAFKA_PRODUCER_BATCH_SIZE=32768
KAFKA_PRODUCER_LINGER_MS=50

# Adjust compression
KAFKA_PRODUCER_COMPRESSION_TYPE=snappy  # or lz4, zstd
```

### Consumer

```python
# Increase poll size
KAFKA_CONSUMER_MAX_POLL_RECORDS=1000

# Tune session timeout
KAFKA_CONSUMER_SESSION_TIMEOUT_MS=30000
```

## Security (Future Enhancement)

- SSL/TLS encryption
- SASL authentication
- ACL-based authorization
- Schema Registry authentication

## References

- Kafka Library: `libs/kafka/README.md`
- Event Schemas: `libs/kafka/src/kafka/events/`
- Producer Examples: `apps/backend-api/src/backend_api/services/kafka_service.py`
- Consumer Examples: `apps/recommendation-api/src/recommendation_api/consumers/`
- Monitoring: `infra/monitoring/grafana/dashboards/kafka-overview.json`
