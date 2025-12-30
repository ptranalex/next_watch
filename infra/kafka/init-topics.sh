#!/bin/bash
# Kafka Topic Initialization Script
# Creates all required topics with appropriate partitioning

set -e

echo "Waiting for Kafka to be ready..."
sleep 30

KAFKA_BROKER="kafka:9092"

# Function to create topic if it doesn't exist
create_topic() {
    local topic=$1
    local partitions=$2
    local replication=$3
    local retention_hours=$4

    echo "Creating topic: $topic (partitions=$partitions, replication=$replication, retention=${retention_hours}h)"

    kafka-topics --bootstrap-server $KAFKA_BROKER \
        --create \
        --if-not-exists \
        --topic $topic \
        --partitions $partitions \
        --replication-factor $replication \
        --config retention.ms=$((retention_hours * 3600000)) \
        --config compression.type=snappy \
        --config cleanup.policy=delete
}

# User Events - Authentication and profile changes
create_topic "user.events" 8 1 168  # 7 days retention

# User Activity - High-volume user interactions with movies
create_topic "user.activity" 16 1 168  # 7 days retention

# Content Updates - Movie metadata changes
create_topic "content.updates" 4 1 720  # 30 days retention

# Cache Invalidation - Cache invalidation events across services
create_topic "cache.invalidation" 8 1 24  # 1 day retention

# Recommendation Requests - Async recommendation generation
create_topic "recommendation.requests" 8 1 72  # 3 days retention

# ML Training - Model retraining triggers
create_topic "ml.training" 4 1 168  # 7 days retention

# System Events - Health checks and service status
create_topic "system.events" 2 1 168  # 7 days retention

# Dead Letter Queue - Failed message processing
create_topic "dlq.events" 4 1 720  # 30 days retention (keep for debugging)

echo "All topics created successfully!"

# List all topics
echo ""
echo "Current topics:"
kafka-topics --bootstrap-server $KAFKA_BROKER --list

echo ""
echo "Topic details:"
kafka-topics --bootstrap-server $KAFKA_BROKER --describe
