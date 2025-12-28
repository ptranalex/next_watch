***REMOVED*** NextWatch Monitoring Scripts

This directory contains deployment scripts for the NextWatch monitoring stack.

***REMOVED******REMOVED*** Local Development Deployment

***REMOVED******REMOVED******REMOVED*** Quick Start

```bash
***REMOVED*** Deploy monitoring stack locally
./deploy-monitoring-local.sh
```

***REMOVED******REMOVED******REMOVED*** What Gets Deployed

The local monitoring stack includes:

- **Prometheus** (http://localhost:9090) - Metrics collection and alerting
- **Grafana** (http://localhost:3001) - Dashboards and visualization
- **AlertManager** (http://localhost:9093) - Alert management
- **Loki** (http://localhost:3100) - Log aggregation
- **Promtail** - Log shipping to Loki
- **Tempo** (http://localhost:3200) - Distributed tracing
- **Blackbox Exporter** (http://localhost:9115) - Health endpoint monitoring
- **Node Exporter** (http://localhost:9100) - System metrics
- **cAdvisor** (http://localhost:8080) - Container metrics

***REMOVED******REMOVED******REMOVED*** Prerequisites

- Docker and Docker Compose installed
- NextWatch services running on standard ports:
  - Backend API: http://localhost:8000
  - BFF API: http://localhost:8001
  - Auth API: http://localhost:8002
  - Search API: http://localhost:8003
  - ML API: http://localhost:8004
  - Recommendation API: http://localhost:8005

***REMOVED******REMOVED******REMOVED*** Configuration

The script automatically creates local configuration files:

- `monitoring/prometheus/prometheus.local.yml` - Prometheus config with localhost targets
- `monitoring/alertmanager/alertmanager.local.yml` - AlertManager config for local alerts
- `monitoring/loki/loki.local.yml` - Loki configuration for log aggregation
- `monitoring/promtail/promtail.local.yml` - Promtail configuration for log shipping
- `monitoring/tempo/tempo.local.yml` - Tempo configuration for tracing

***REMOVED******REMOVED******REMOVED*** Management Commands

```bash
***REMOVED*** View logs
docker compose -f infra/compose/monitoring.local.yml logs -f

***REMOVED*** Restart services
docker compose -f infra/compose/monitoring.local.yml restart

***REMOVED*** Stop monitoring
docker compose -f infra/compose/monitoring.local.yml down

***REMOVED*** Clean up (removes volumes)
docker compose -f infra/compose/monitoring.local.yml down -v
```

***REMOVED******REMOVED******REMOVED*** Accessing Services

- **Grafana**: http://localhost:3001 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093
- **Loki**: http://localhost:3100
- **Tempo**: http://localhost:3200

***REMOVED******REMOVED******REMOVED*** Health Status Monitoring

The local deployment includes the enhanced health status monitoring that supports:

- **Healthy** - All systems operational
- **Degraded** - Critical services up, some non-critical services down
- **Unhealthy** - Critical services down

Use these Grafana queries for your charts:

```promql
***REMOVED*** Healthy services
probe_success{job="nextwatch-health-healthy-only"}

***REMOVED*** Degraded services
probe_success{job="nextwatch-health-degraded-only"}

***REMOVED*** Enhanced status overview
probe_success{job="nextwatch-health-healthy-only"} * 3 +
probe_success{job="nextwatch-health-degraded-only"} * 2 +
(probe_success{job="nextwatch-health-endpoints"}
  and probe_success{job="nextwatch-health-healthy-only"} == 0
  and probe_success{job="nextwatch-health-degraded-only"} == 0) * 1
```

***REMOVED******REMOVED******REMOVED*** Troubleshooting

1. **Services not starting**: Check Docker is running and ports are available
2. **No metrics**: Ensure NextWatch services are running on expected ports
3. **Permission issues**: The script tries to set Docker socket permissions
4. **Log collection issues**: Verify NextWatch service log volumes exist

***REMOVED******REMOVED******REMOVED*** Production Deployment

For production deployment, use:

```bash
***REMOVED*** AWS production deployment
./aws/deployment/deploy-monitoring-one-click.sh
```

***REMOVED******REMOVED*** 🔍 Service Status Checking

***REMOVED******REMOVED******REMOVED*** check-services.sh

Comprehensive health check script that monitors all Next Watch services and infrastructure.

**Usage:**

```bash
./infra/scripts/check-services.sh
```

**What it checks:**

- **Infrastructure Services:** Redis (Homebrew), Qdrant (Docker)
- **Application Services:** All APIs (Backend, BFF, Recommendation, Auth, ML, Search) + Frontend
- **Docker Containers:** NextWatch container status
- **Homebrew Services:** Redis service status

**Example Output:**

```
🔍 Checking Next Watch Services Status...

🏗️ Infrastructure Services:
✅ Redis (Homebrew) - UP (localhost:6379)
✅ Qdrant (Docker) - UP (localhost:6333)

🚀 Application Services:
✅ Backend API - UP
✅ BFF API - UP
...
```

Used by the TMUX development environment monitoring window.
