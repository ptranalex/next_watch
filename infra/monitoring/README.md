# NextWatch Monitoring Stack

## Overview

This directory contains the monitoring configuration for the NextWatch platform, including Prometheus, Grafana, and Alertmanager.

## Health Status Monitoring

### Health Status Types

Our services support three health status types:

1. **Healthy** (`"status": "healthy"`) - All systems operational
2. **Degraded** (`"status": "degraded"`) - Critical services up, some non-critical services down
3. **Unhealthy** (`"status": "unhealthy"`) - Critical services down

### Monitoring Configuration

#### Blackbox Exporter Modules

- `http_health` - Accepts both 200 and 503 status codes (basic up/down)
- `http_health_healthy_only` - Only passes when JSON contains `"status": "healthy"`
- `http_health_degraded_only` - Only passes when JSON contains `"status": "degraded"`
- `http_readiness` - Readiness checks (must be 200)

#### Prometheus Jobs

1. **nextwatch-health-endpoints** - Basic health monitoring (up/down)
2. **nextwatch-health-healthy-only** - Tracks services in healthy state
3. **nextwatch-health-degraded-only** - Tracks services in degraded state
4. **nextwatch-readiness-endpoints** - Readiness monitoring for traffic routing

### Querying Health Status

#### Check if service is healthy:

```promql
probe_success{job="nextwatch-health-healthy-only", service="backend-api"}
```

#### Check if service is degraded:

```promql
probe_success{job="nextwatch-health-degraded-only", service="backend-api"}
```

#### Count services by status:

```promql
# Healthy services
sum(probe_success{job="nextwatch-health-healthy-only"})

# Degraded services
sum(probe_success{job="nextwatch-health-degraded-only"})

# Total responsive services (healthy + degraded)
sum(probe_success{job="nextwatch-health-endpoints"})
```

#### Alert on degraded services:

```promql
# Alert when any service is degraded
probe_success{job="nextwatch-health-degraded-only"} == 1

# Alert when service is neither healthy nor degraded (unhealthy)
probe_success{job="nextwatch-health-endpoints"} == 1
  and probe_success{job="nextwatch-health-healthy-only"} == 0
  and probe_success{job="nextwatch-health-degraded-only"} == 0
```

### Service Health Behavior

- **HTTP 200 + "healthy"**: Service fully operational
- **HTTP 200 + "degraded"**: Service operational but some dependencies down
- **HTTP 503 + "degraded"**: Service operational but significant dependencies down
- **HTTP 503 + "unhealthy"**: Service critical dependencies down
- **No response**: Service completely down

## Configuration Files

### Single Source of Truth

- **`prometheus/prometheus.yml`** - Main Prometheus configuration that works for both development and production

### Removed Files (Consolidated)

- ~~`prometheus/prometheus.prod.yml`~~ - Merged into main config
- ~~`prometheus/prometheus.aws.yml`~~ - Merged into main config

## How It Works

### Multi-Target Configuration

The unified `prometheus.yml` uses a smart approach with multiple targets per job:

```yaml
- job_name: "nextwatch-backend-api"
  static_configs:
    - targets: ["host.docker.internal:8000", "backend-api:8000"]
```

This allows:

- **Development**: Uses `host.docker.internal:PORT` when services run on host
- **Production**: Uses `container-name:PORT` when services run in containers
- **AWS/Cloud**: Uses `host.docker.internal:PORT` with proper Docker host mapping

### Docker Configuration

The `infra/compose/monitoring.yml` includes:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

This makes `host.docker.internal` work on Linux systems (AWS/cloud).

## Deployment

### Development

```bash
docker compose -f infra/compose/monitoring.yml up -d
```

### Production/AWS

```bash
# Deploy the monitoring stack on AWS (one-click)
./infra/aws/deployment/deploy-monitoring-one-click.sh
```

## Service Discovery

### NextWatch Services (Internal Container Ports)

- **backend-api**: Port 8000 (external: 8000)
- **bff-api**: Port 8000 (external: 8001)
- **recommendation-api**: Port 8000 (external: 8002)
- **auth-api**: Port 8000 (external: 8003)
- **ml-api**: Port 8000 (external: 8004)
- **search-api**: Port 8000 (external: 8005)

Note: All NextWatch API services now use internal port 8000 for standardization. External ports remain unchanged for backwards compatibility.

### Infrastructure Services

- **node-exporter**: Port 9100 (system metrics)
- **cadvisor**: Port 8080 (container metrics)
- **alertmanager**: Port 9093 (alerts)
- **grafana**: Port 3000 (dashboards)

## Verification

1. **Prometheus UI**: http://localhost:9090/targets
2. **Grafana**: http://localhost:3001
3. **Check metrics**: `curl http://localhost:9090/api/v1/query?query=up`

## Troubleshooting

### Common Issues

1. **Services showing as DOWN**: Check if the service is running on the expected port
2. **host.docker.internal not working**: Ensure `extra_hosts` is configured in Docker Compose
3. **No metrics**: Verify the service has `/metrics` endpoint enabled

### Debug Commands

```bash
# Check Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .job, health: .health}'

# Test service metrics (using external ports for localhost access)
curl http://localhost:8000/metrics  # backend-api
curl http://localhost:8001/metrics  # bff-api (external port maps to internal 8000)

# Check Docker host resolution
docker exec prometheus-prod nslookup host.docker.internal
```
