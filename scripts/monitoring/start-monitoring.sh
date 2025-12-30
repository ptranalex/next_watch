#!/bin/bash
# NextWatch Monitoring Stack Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
INFRA_DIR="$PROJECT_ROOT/infra"
MONITORING_DIR="$INFRA_DIR/monitoring"

echo -e "${BLUE}🚀 Starting NextWatch Monitoring Stack${NC}"
echo "Project root: $PROJECT_ROOT"

# Create directories if they don't exist
echo -e "${YELLOW}📁 Creating monitoring directories...${NC}"
mkdir -p "$MONITORING_DIR/prometheus/rules"
mkdir -p "$MONITORING_DIR/grafana/provisioning/datasources"
mkdir -p "$MONITORING_DIR/grafana/provisioning/dashboards"
mkdir -p "$MONITORING_DIR/grafana/dashboards/nextwatch"
mkdir -p "$MONITORING_DIR/grafana/dashboards/infrastructure"
mkdir -p "$MONITORING_DIR/grafana/dashboards/business"
mkdir -p "$MONITORING_DIR/alertmanager"

# Set proper permissions
echo -e "${YELLOW}🔒 Setting permissions...${NC}"
chmod -R 755 "$MONITORING_DIR"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if docker-compose is available
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echo -e "${RED}❌ Neither 'docker compose' nor 'docker-compose' found. Please install Docker Compose.${NC}"
    exit 1
fi

# Create network if it doesn't exist
echo -e "${YELLOW}🌐 Creating Docker network...${NC}"
docker network create nextwatch-network 2>/dev/null || echo "Network already exists"

# Start monitoring stack
echo -e "${YELLOW}🐳 Starting monitoring containers...${NC}"
cd "$INFRA_DIR"

# Stop any existing containers
$DOCKER_COMPOSE_CMD -f "$INFRA_DIR/compose/monitoring.yml" down

# Start the stack
$DOCKER_COMPOSE_CMD -f "$INFRA_DIR/compose/monitoring.yml" up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"

check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    echo -n "Checking $service_name"
    while [ $attempt -le $max_attempts ]; do
        if curl -sf "$url" >/dev/null 2>&1; then
            echo -e " ${GREEN}✅${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done
    echo -e " ${RED}❌ Failed to start${NC}"
    return 1
}

# Check Prometheus
check_service "Prometheus" "http://localhost:9090/-/healthy"

# Check Grafana
check_service "Grafana" "http://localhost:3001/api/health"

# Check AlertManager
check_service "AlertManager" "http://localhost:9093/-/healthy"

# Display status
echo -e "\n${GREEN}🎉 Monitoring stack is running!${NC}"
echo ""
echo -e "${BLUE}📊 Access URLs:${NC}"
echo -e "  Grafana:      ${GREEN}http://localhost:3001${NC} (admin/admin123)"
echo -e "  Prometheus:   ${GREEN}http://localhost:9090${NC}"
echo -e "  AlertManager: ${GREEN}http://localhost:9093${NC}"
echo ""

# Check for NextWatch services
echo -e "${BLUE}🔍 Checking NextWatch services...${NC}"
services_found=false

check_nextwatch_service() {
    local service_name=$1
    local port=$2

    if curl -sf "http://localhost:$port/metrics" >/dev/null 2>&1; then
        echo -e "  $service_name: ${GREEN}✅ Running with metrics${NC}"
        services_found=true
    else
        echo -e "  $service_name: ${YELLOW}⚠️  Not running${NC}"
    fi
}

check_nextwatch_service "BFF API" "8001"
check_nextwatch_service "Backend API" "8002"
check_nextwatch_service "Auth API" "8003"
check_nextwatch_service "Search API" "8004"
check_nextwatch_service "Recommendation API" "8005"
check_nextwatch_service "ML API" "8006"

if [ "$services_found" = false ]; then
    echo ""
    echo -e "${YELLOW}ℹ️  No NextWatch services detected.${NC}"
    echo -e "   Start your services with metrics enabled to see data in Grafana."
    echo ""
    echo -e "${BLUE}Example:${NC}"
    echo -e "  cd apps/bff-api && hatch shell && python -m bff_api.main"
fi

echo ""
echo -e "${GREEN}✨ Setup complete! Happy monitoring! ✨${NC}"
echo ""
echo -e "${BLUE}📖 Documentation:${NC} docs/observability/PROMETHEUS_GRAFANA_SETUP.md"
echo -e "${BLUE}🐛 Logs:${NC} $DOCKER_COMPOSE_CMD -f $INFRA_DIR/compose/monitoring.yml logs -f"
