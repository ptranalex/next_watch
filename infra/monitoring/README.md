***REMOVED*** NextWatch Monitoring Configuration

***REMOVED******REMOVED*** Overview

This directory contains the unified monitoring configuration for NextWatch using Prometheus, Grafana, and related tools.

***REMOVED******REMOVED*** Configuration Files

***REMOVED******REMOVED******REMOVED*** Single Source of Truth

- **`prometheus/prometheus.yml`** - Main Prometheus configuration that works for both development and production

***REMOVED******REMOVED******REMOVED*** Removed Files (Consolidated)

- ~~`prometheus/prometheus.prod.yml`~~ - Merged into main config
- ~~`prometheus/prometheus.aws.yml`~~ - Merged into main config

***REMOVED******REMOVED*** How It Works

***REMOVED******REMOVED******REMOVED*** Multi-Target Configuration

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

***REMOVED******REMOVED******REMOVED*** Docker Configuration

The `docker-compose.monitoring.yml` includes:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

This makes `host.docker.internal` work on Linux systems (AWS/cloud).

***REMOVED******REMOVED*** Deployment

***REMOVED******REMOVED******REMOVED*** Development

```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

***REMOVED******REMOVED******REMOVED*** Production/AWS

```bash
cd infra/
./scripts/fix-metrics-aws.sh
```

***REMOVED******REMOVED*** Service Discovery

***REMOVED******REMOVED******REMOVED*** NextWatch Services (Internal Container Ports)

- **backend-api**: Port 8000 (external: 8000)
- **bff-api**: Port 8000 (external: 8001)
- **recommendation-api**: Port 8000 (external: 8002)
- **auth-api**: Port 8000 (external: 8003)
- **ml-api**: Port 8000 (external: 8004)
- **search-api**: Port 8000 (external: 8005)

Note: All NextWatch API services now use internal port 8000 for standardization. External ports remain unchanged for backwards compatibility.

***REMOVED******REMOVED******REMOVED*** Infrastructure Services

- **node-exporter**: Port 9100 (system metrics)
- **cadvisor**: Port 8080 (container metrics)
- **alertmanager**: Port 9093 (alerts)
- **grafana**: Port 3000 (dashboards)

***REMOVED******REMOVED*** Verification

1. **Prometheus UI**: http://localhost:9090/targets
2. **Grafana**: http://localhost:3001
3. **Check metrics**: `curl http://localhost:9090/api/v1/query?query=up`

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Common Issues

1. **Services showing as DOWN**: Check if the service is running on the expected port
2. **host.docker.internal not working**: Ensure `extra_hosts` is configured in docker-compose
3. **No metrics**: Verify the service has `/metrics` endpoint enabled

***REMOVED******REMOVED******REMOVED*** Debug Commands

```bash
***REMOVED*** Check Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .job, health: .health}'

***REMOVED*** Test service metrics (using external ports for localhost access)
curl http://localhost:8000/metrics  ***REMOVED*** backend-api
curl http://localhost:8001/metrics  ***REMOVED*** bff-api (external port maps to internal 8000)

***REMOVED*** Check Docker host resolution
docker exec prometheus-prod nslookup host.docker.internal
```
