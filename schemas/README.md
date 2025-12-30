# Event Schemas

This directory contains all Kafka event schemas in Avro format (`.avsc`).

## Schema Naming Convention

Format: `<event-type>.v<version>.avsc`

Examples:
- `user.registered.v1.avsc`
- `movie.viewed.v1.avsc`

## Schema Evolution

- **Breaking changes**: Increment version (v1 → v2)
- **Non-breaking changes**: Update existing version
- **Always check compatibility** before deploying

## Registering Schemas

```bash
# From any service with kafka library installed
cd /path/to/service
hatch shell
python -m kafka.cli.register_schemas register --schema-dir ../../schemas
```

## Consuming from Other Languages

### Go

```go
import (
    "github.com/confluentinc/confluent-kafka-go/kafka"
    "github.com/confluentinc/confluent-kafka-go/schemaregistry"
)

// Create Schema Registry client
srClient, _ := schemaregistry.NewClient(schemaregistry.NewConfig(
    "http://localhost:8081"))

// Create Kafka consumer
consumer, _ := kafka.NewConsumer(&kafka.ConfigMap{
    "bootstrap.servers": "localhost:9093",
    "group.id":          "go-consumer",
})

consumer.Subscribe([]string{"user.activity"}, nil)

// Avro deserializer automatically fetches schema from registry
// Messages are decoded automatically!
```

### Node.js

```javascript
const { SchemaRegistry } = require('@kafkajs/confluent-schema-registry')
const { Kafka } = require('kafkajs')

const registry = new SchemaRegistry({ host: 'http://localhost:8081' })
const kafka = new Kafka({ brokers: ['localhost:9093'] })

const consumer = kafka.consumer({ groupId: 'node-consumer' })
await consumer.connect()
await consumer.subscribe({ topic: 'user.activity' })

await consumer.run({
  eachMessage: async ({ message }) => {
    const decoded = await registry.decode(message.value)
    console.log(decoded) // Automatically decoded event
  },
})
```

## Schema Structure

All events inherit base fields:
- `event_id`: Unique event identifier
- `event_type`: Type of the event
- `timestamp`: Event timestamp in UTC (milliseconds)
- `service_name`: Service that emitted the event
- `trace_id`: Distributed tracing trace ID
- `span_id`: Distributed tracing span ID
- `metadata`: Additional event metadata (map)

## Available Events

### User Events
- `user.registered` - New user registration
- `user.login` - User login event
- `user.logout` - User logout event

### Activity Events
- `movie.viewed` - User views a movie
- `movie.rated` - User rates a movie
- `watchlist.changed` - User modifies watchlist

### Content Events
- `movie.created` - New movie added to catalog
- `movie.updated` - Movie metadata updated
- `movie.deleted` - Movie removed from catalog

### System Events
- `cache.invalidation` - Cache invalidation request
- `recommendation.request` - Async recommendation generation
- `ml.training` - ML model retraining trigger
- `system.health` - Service health status change
- `dlq.event` - Dead letter queue event
