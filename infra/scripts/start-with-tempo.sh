#!/bin/bash

# Start services with Tempo dependency management
# This script ensures Tempo is healthy before starting application services

set -e

echo "🚀 Starting NextWatch services with Tempo dependency management..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INFRA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echo "❌ Neither 'docker compose' nor 'docker-compose' found. Please install Docker Compose."
    exit 1
fi

# Function to check if Tempo is ready
check_tempo_ready() {
    local max_attempts=30
    local attempt=1

    echo "⏳ Waiting for Tempo to be ready..."

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f http://localhost:3200/ready > /dev/null 2>&1; then
            echo "✅ Tempo is ready!"
            return 0
        fi

        echo "⏱️  Attempt $attempt/$max_attempts: Tempo not ready yet, waiting 5 seconds..."
        sleep 5
        ((attempt++))
    done

    echo "❌ Tempo failed to become ready after $max_attempts attempts"
    return 1
}

# Function to check if Tempo container exists and is running
check_tempo_container() {
    if ! docker ps --format "table {{.Names}}" | grep -q "tempo-"; then
        echo "❌ Tempo container not found. Please start the monitoring stack first:"
        echo "   $DOCKER_COMPOSE_CMD -f $INFRA_DIR/compose/monitoring.local.yml up -d tempo"
        exit 1
    fi

    if ! docker ps --format "table {{.Names}}\t{{.Status}}" | grep "tempo-" | grep -q "healthy"; then
        echo "⚠️  Tempo container exists but may not be healthy yet..."
    fi
}

# Check if Tempo container exists
check_tempo_container

# Wait for Tempo to be ready
if check_tempo_ready; then
    echo "🎯 Starting application services..."

    # Start services in order with dependencies
    cd "$INFRA_DIR"

    if [ "$1" = "prod" ]; then
        echo "🏭 Starting production services..."
        $DOCKER_COMPOSE_CMD -f "$INFRA_DIR/compose/prod.yml" up -d
    else
        echo "🧪 Starting development services..."
        echo "Please specify which services to start or use existing compose files"
        echo "Example: $DOCKER_COMPOSE_CMD -f $INFRA_DIR/compose/prod.yml up -d backend-api"
    fi

    echo "✅ Services started successfully!"
    echo "🔍 Check service logs: docker logs <service-name>"
    echo "📊 Grafana: http://localhost:3001"
    echo "🔎 Tempo: http://localhost:3200"

else
    echo "❌ Failed to start services - Tempo is not ready"
    exit 1
fi
