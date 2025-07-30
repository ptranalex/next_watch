***REMOVED***!/bin/bash

***REMOVED*** NextWatch Monitoring Stack - Local Development Deployment

set -e

***REMOVED*** Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' ***REMOVED*** No Color

***REMOVED*** Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$INFRA_DIR")"

echo -e "${BLUE}🚀 NextWatch Monitoring Stack - Local Development Deployment${NC}"
echo "============================================================================"
echo ""
echo "This script will deploy the complete NextWatch monitoring stack locally:"
echo "  📊 Prometheus (Metrics Collection)"
echo "  📈 Grafana (Dashboards & Visualization)"
echo "  🔔 AlertManager (Alert Management)"
echo "  📋 Loki (Log Aggregation)"
echo "  🚚 Promtail (Log Shipping)"
echo "  🔍 Tempo (Distributed Tracing)"
echo "  🏥 Blackbox Exporter (Health Monitoring)"
echo "  📊 Node Exporter (System Metrics)"
echo "  🐳 cAdvisor (Container Metrics)"
echo ""

***REMOVED*** Confirmation
read -p "Continue with local monitoring deployment? [y/N]: " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Step 1/6: Environment Check${NC}"
echo -e "${YELLOW}========================================${NC}"

***REMOVED*** Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"

***REMOVED*** Check if Docker Compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose is available${NC}"

***REMOVED*** Check if NextWatch network exists
if ! docker network ls | grep -q "next_watch_default"; then
    echo -e "${YELLOW}⚠️  NextWatch network not found. Creating it...${NC}"
    docker network create next_watch_default
    echo -e "${GREEN}✅ NextWatch network created${NC}"
else
    echo -e "${GREEN}✅ NextWatch network exists${NC}"
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Step 2/6: Configuration Setup${NC}"
echo -e "${YELLOW}========================================${NC}"

***REMOVED*** Create necessary configuration files for local development
cd "$INFRA_DIR"

***REMOVED*** Create local environment file if it doesn't exist
if [ ! -f ".env.monitoring.local" ]; then
    echo "***REMOVED*** Local Monitoring Environment" > .env.monitoring.local
    echo "GRAFANA_ADMIN_PASSWORD=admin123" >> .env.monitoring.local
    echo "GRAFANA_SECRET_KEY=local-secret-key" >> .env.monitoring.local
    echo -e "${GREEN}✅ Created local monitoring environment file${NC}"
else
    echo -e "${GREEN}✅ Local monitoring environment file exists${NC}"
fi

***REMOVED*** Check for required configuration files and create them if missing
echo "🔧 Checking configuration files..."

***REMOVED*** Create local AlertManager config if it doesn't exist
if [ ! -f "monitoring/alertmanager/alertmanager.local.yml" ]; then
    echo "Creating local AlertManager configuration..."
    cat > monitoring/alertmanager/alertmanager.local.yml << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'nextwatch-local@localhost'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://localhost:5001/webhook'
    send_resolved: true

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
EOF
    echo -e "${GREEN}✅ Created local AlertManager configuration${NC}"
fi

***REMOVED*** Create local Loki config if it doesn't exist
if [ ! -f "monitoring/loki/loki.local.yml" ]; then
    echo "Creating local Loki configuration..."
    cat > monitoring/loki/loki.local.yml << 'EOF'
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  instance_addr: 127.0.0.1
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093

limits_config:
  reject_old_samples: true
  reject_old_samples_max_age: 168h

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: false
  retention_period: 0s

compactor:
  working_directory: /loki/boltdb-shipper-compactor
  shared_store: filesystem
  compaction_interval: 10m
  retention_enabled: true
  retention_delete_delay: 2h
  retention_delete_worker_count: 150

ingester:
  max_chunk_age: 1h
  chunk_idle_period: 5m
  chunk_block_size: 262144
  chunk_retain_period: 1m
  max_transfer_retries: 0
  wal:
    enabled: true
    dir: /loki/wal
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
    final_sleep: 0s
  chunk_encoding: snappy

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    cache_ttl: 24h
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

frontend:
  log_queries_longer_than: 5s
  compress_responses: true
  tail_proxy_url: http://127.0.0.1:3100
EOF
    echo -e "${GREEN}✅ Created local Loki configuration${NC}"
fi

***REMOVED*** Create local Promtail config if it doesn't exist
if [ ! -f "monitoring/promtail/promtail.local.yml" ]; then
    echo "Creating local Promtail configuration..."
    cat > monitoring/promtail/promtail.local.yml << 'EOF'
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki-local:3100/loki/api/v1/push

scrape_configs:
  ***REMOVED*** Docker container logs
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
        filters:
          - name: label
            values: ["logging=promtail"]
    relabel_configs:
      - source_labels: ['__meta_docker_container_name']
        regex: '/(.*)'
        target_label: 'container'
      - source_labels: ['__meta_docker_container_log_stream']
        target_label: 'logstream'
      - source_labels: ['__meta_docker_container_label_logging']
        target_label: 'logging'
    pipeline_stages:
      - json:
          expressions:
            level: level
            logger: logger
            message: message
            timestamp: timestamp
      - labels:
          level:
          logger:
      - timestamp:
          source: timestamp
          format: RFC3339Nano
      - output:
          source: message

  ***REMOVED*** NextWatch service logs from volumes
  - job_name: nextwatch-backend
    static_configs:
      - targets:
          - localhost
        labels:
          job: nextwatch-backend
          service: backend-api
          __path__: /app/logs/backend/*.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            message: message
            timestamp: timestamp
            service: service
      - labels:
          level:
          service:
      - timestamp:
          source: timestamp
          format: RFC3339Nano

  - job_name: nextwatch-bff
    static_configs:
      - targets:
          - localhost
        labels:
          job: nextwatch-bff
          service: bff-api
          __path__: /app/logs/bff/*.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            message: message
            timestamp: timestamp
            service: service
      - labels:
          level:
          service:
      - timestamp:
          source: timestamp
          format: RFC3339Nano

  - job_name: nextwatch-auth
    static_configs:
      - targets:
          - localhost
        labels:
          job: nextwatch-auth
          service: auth-api
          __path__: /app/logs/auth/*.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            message: message
            timestamp: timestamp
            service: service
      - labels:
          level:
          service:
      - timestamp:
          source: timestamp
          format: RFC3339Nano

  - job_name: nextwatch-search
    static_configs:
      - targets:
          - localhost
        labels:
          job: nextwatch-search
          service: search-api
          __path__: /app/logs/search/*.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            message: message
            timestamp: timestamp
            service: service
      - labels:
          level:
          service:
      - timestamp:
          source: timestamp
          format: RFC3339Nano

  - job_name: nextwatch-recommendation
    static_configs:
      - targets:
          - localhost
        labels:
          job: nextwatch-recommendation
          service: recommendation-api
          __path__: /app/logs/recommendation/*.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            message: message
            timestamp: timestamp
            service: service
      - labels:
          level:
          service:
      - timestamp:
          source: timestamp
          format: RFC3339Nano

  - job_name: nextwatch-ml
    static_configs:
      - targets:
          - localhost
        labels:
          job: nextwatch-ml
          service: ml-api
          __path__: /app/logs/ml/*.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            message: message
            timestamp: timestamp
            service: service
      - labels:
          level:
          service:
      - timestamp:
          source: timestamp
          format: RFC3339Nano

  ***REMOVED*** System logs
  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: varlogs
          __path__: /var/log/*.log
EOF
    echo -e "${GREEN}✅ Created local Promtail configuration${NC}"
fi

***REMOVED*** Create local Tempo config if it doesn't exist
if [ ! -f "monitoring/tempo/tempo.local.yml" ]; then
    echo "Creating local Tempo configuration..."
    cat > monitoring/tempo/tempo.local.yml << 'EOF'
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318
    zipkin:
      endpoint: 0.0.0.0:9411
    jaeger:
      protocols:
        thrift_http:
          endpoint: 0.0.0.0:14268

ingester:
  trace_idle_period: 10s
  max_block_bytes: 1_000_000
  max_block_duration: 5m

compactor:
  compaction:
    compaction_window: 1h
    max_block_bytes: 100_000_000
    block_retention: 1h
    compacted_block_retention: 10m

storage:
  trace:
    backend: local
    local:
      path: /tmp/tempo/traces
    wal:
      path: /tmp/tempo/wal
    pool:
      max_workers: 100
      queue_depth: 10000

querier:
  frontend_worker:
    frontend_address: tempo-local:9095

query_frontend:
  search:
    duration_slo: 5s
    throughput_bytes_slo: 1.073741824e+09
  trace_by_id:
    duration_slo: 5s

metrics_generator:
  registry:
    external_labels:
      source: tempo
      cluster: docker-compose
  storage:
    path: /tmp/tempo/generator/wal
    remote_write:
      - url: http://prometheus-local:9090/api/v1/write
        send_exemplars: true
EOF
    echo -e "${GREEN}✅ Created local Tempo configuration${NC}"
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Step 3/6: Updating Prometheus Config${NC}"
echo -e "${YELLOW}========================================${NC}"

***REMOVED*** Create a local version of Prometheus config with localhost targets
if [ ! -f "monitoring/prometheus/prometheus.local.yml" ]; then
    echo "Creating local Prometheus configuration..."
    ***REMOVED*** Copy the main prometheus.yml and modify for local development
    cp monitoring/prometheus/prometheus.yml monitoring/prometheus/prometheus.local.yml
    
    ***REMOVED*** Replace service hostnames with localhost for local development
    sed -i.bak 's/backend-api:8000/localhost:8000/g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's/bff-api:8000/localhost:8001/g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's/auth-api:8000/localhost:8002/g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's/search-api:8000/localhost:8003/g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's/ml-api:8000/localhost:8004/g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's/recommendation-api:8000/localhost:8005/g' monitoring/prometheus/prometheus.local.yml
    
    ***REMOVED*** Update health check URLs for local development
    sed -i.bak 's|http://backend-api:8000/health|http://localhost:8000/health|g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's|http://bff-api:8000/health|http://localhost:8001/health|g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's|http://auth-api:8000/health|http://localhost:8002/health|g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's|http://search-api:8000/health|http://localhost:8003/health|g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's|http://ml-api:8000/health|http://localhost:8004/health|g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's|http://recommendation-api:8000/health|http://localhost:8005/health|g' monitoring/prometheus/prometheus.local.yml
    
    ***REMOVED*** Update readiness check URLs
    sed -i.bak 's|http://backend-api:8000/health/ready|http://localhost:8000/health/ready|g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's|http://bff-api:8000/health/ready|http://localhost:8001/health/ready|g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's|http://auth-api:8000/health/ready|http://localhost:8002/health/ready|g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's|http://search-api:8000/health/ready|http://localhost:8003/health/ready|g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's|http://ml-api:8000/health/ready|http://localhost:8004/health/ready|g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's|http://recommendation-api:8000/health/ready|http://localhost:8005/health/ready|g' monitoring/prometheus/prometheus.local.yml
    
    ***REMOVED*** Update TCP connectivity checks
    sed -i.bak 's/backend-api:8000/localhost:8000/g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's/bff-api:8000/localhost:8001/g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's/auth-api:8000/localhost:8002/g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's/search-api:8000/localhost:8003/g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's/ml-api:8000/localhost:8004/g' monitoring/prometheus/prometheus.local.yml
    sed -i.bak 's/recommendation-api:8000/localhost:8005/g' monitoring/prometheus/prometheus.local.yml
    
    ***REMOVED*** Update environment label to local
    sed -i.bak 's/production/local/g' monitoring/prometheus/prometheus.local.yml
    
    ***REMOVED*** Clean up backup files
    rm -f monitoring/prometheus/prometheus.local.yml.bak
    
    echo -e "${GREEN}✅ Created local Prometheus configuration${NC}"
fi

***REMOVED*** Update the docker-compose to use local prometheus config
sed -i.bak 's|./monitoring/prometheus/:/etc/prometheus/|./monitoring/prometheus/prometheus.local.yml:/etc/prometheus/prometheus.yml:ro|g' docker-compose.monitoring.local.yml
rm -f docker-compose.monitoring.local.yml.bak

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Step 4/6: Stopping Existing Services${NC}"
echo -e "${YELLOW}========================================${NC}"

***REMOVED*** Stop any existing monitoring services
echo "🛑 Stopping existing monitoring services..."
docker-compose -f docker-compose.monitoring.local.yml down --remove-orphans 2>/dev/null || true
echo -e "${GREEN}✅ Stopped existing services${NC}"

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Step 5/6: Deploying Monitoring Stack${NC}"
echo -e "${YELLOW}========================================${NC}"

***REMOVED*** Deploy the monitoring stack
echo "🚀 Starting monitoring stack..."
docker-compose -f docker-compose.monitoring.local.yml up -d

***REMOVED*** Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

***REMOVED*** Check service health
echo "🏥 Checking service health..."
services_ready=0
max_attempts=12
attempt=0

while [ $services_ready -eq 0 ] && [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))
    echo "  Attempt $attempt/$max_attempts..."
    
    ***REMOVED*** Check Prometheus
    if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
        echo -e "    ${GREEN}✅ Prometheus is healthy${NC}"
        prometheus_ready=1
    else
        echo -e "    ${YELLOW}⏳ Prometheus is starting...${NC}"
        prometheus_ready=0
    fi
    
    ***REMOVED*** Check Grafana
    if curl -s http://localhost:3001/api/health > /dev/null 2>&1; then
        echo -e "    ${GREEN}✅ Grafana is healthy${NC}"
        grafana_ready=1
    else
        echo -e "    ${YELLOW}⏳ Grafana is starting...${NC}"
        grafana_ready=0
    fi
    
    ***REMOVED*** Check Loki
    if curl -s http://localhost:3100/ready > /dev/null 2>&1; then
        echo -e "    ${GREEN}✅ Loki is healthy${NC}"
        loki_ready=1
    else
        echo -e "    ${YELLOW}⏳ Loki is starting...${NC}"
        loki_ready=0
    fi
    
    ***REMOVED*** Check Tempo
    if curl -s http://localhost:3200/ready > /dev/null 2>&1; then
        echo -e "    ${GREEN}✅ Tempo is healthy${NC}"
        tempo_ready=1
    else
        echo -e "    ${YELLOW}⏳ Tempo is starting...${NC}"
        tempo_ready=0
    fi
    
    ***REMOVED*** Check if all services are ready
    if [ $prometheus_ready -eq 1 ] && [ $grafana_ready -eq 1 ] && [ $loki_ready -eq 1 ] && [ $tempo_ready -eq 1 ]; then
        services_ready=1
    else
        sleep 10
    fi
done

if [ $services_ready -eq 1 ]; then
    echo -e "${GREEN}✅ All monitoring services are healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Some services may still be starting. Check logs if needed.${NC}"
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Step 6/6: Final Configuration${NC}"
echo -e "${YELLOW}========================================${NC}"

***REMOVED*** Set proper permissions for Docker socket (for Promtail)
echo "🔧 Setting Docker socket permissions..."
sudo chmod 666 /var/run/docker.sock 2>/dev/null || echo "Note: Could not set Docker socket permissions. Promtail may have limited access."

echo ""
echo -e "${GREEN}🎉 LOCAL MONITORING DEPLOYMENT SUCCESSFUL!${NC}"
echo "================================================================"
echo ""
echo "🌐 Your NextWatch Monitoring Stack is now running locally:"
echo ""
echo "  📊 Grafana Dashboard:       http://localhost:3001"
echo "  🔍 Prometheus Metrics:      http://localhost:9090"
echo "  📢 AlertManager:            http://localhost:9093"
echo "  📋 Loki Logs:               http://localhost:3100"
echo "  🔍 Tempo Tracing:           http://localhost:3200"
echo "  🏥 Blackbox Exporter:       http://localhost:9115"
echo "  📊 Node Exporter:           http://localhost:9100"
echo "  🐳 cAdvisor:                http://localhost:8080"
echo ""
echo "🔐 Login Credentials:"
echo "  Grafana: admin / admin123"
echo ""
echo "🎯 What's Being Monitored:"
echo "  📈 Metrics: All NextWatch services (if running on standard ports)"
echo "  📋 Logs: Docker container logs and NextWatch service logs"
echo "  🔍 Traces: Distributed tracing with Tempo"
echo "  🖥️  System: CPU, Memory, Disk, Network"
echo "  🏥 Health: Service health endpoints with degraded status support"
echo ""
echo "📋 Expected Service Ports:"
echo "  🔹 Backend API:        http://localhost:8000"
echo "  🔹 BFF API:            http://localhost:8001"
echo "  🔹 Auth API:           http://localhost:8002"
echo "  🔹 Search API:         http://localhost:8003"
echo "  🔹 ML API:             http://localhost:8004"
echo "  🔹 Recommendation API: http://localhost:8005"
echo ""
echo "🔧 Management Commands:"
echo "  📊 View logs:          docker-compose -f docker-compose.monitoring.local.yml logs -f"
echo "  🔄 Restart services:   docker-compose -f docker-compose.monitoring.local.yml restart"
echo "  🛑 Stop monitoring:    docker-compose -f docker-compose.monitoring.local.yml down"
echo "  🗑️  Clean up:          docker-compose -f docker-compose.monitoring.local.yml down -v"
echo ""
echo "📈 Your updated Grafana charts should now support:"
echo "  ✅ Healthy status monitoring"
echo "  ⚠️  Degraded status monitoring"
echo "  ❌ Unhealthy status monitoring"
echo ""
echo -e "${GREEN}🎊 Happy Local Monitoring! Your NextWatch observability is ready.${NC}" 