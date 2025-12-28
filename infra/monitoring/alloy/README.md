***REMOVED*** Grafana Alloy Docker Setup for NextWatch

This directory contains the Docker configuration for running Grafana Alloy on AWS to collect metrics and logs for Grafana Cloud migration.

***REMOVED******REMOVED*** 🎯 Quick Start

***REMOVED******REMOVED******REMOVED*** 1. Set Up Grafana Cloud Account (if not done)

1. Go to [grafana.com](https://grafana.com/auth/sign-up)
2. Choose **Free** plan
3. Create stack name: `nextwatch-monitoring`
4. Note your stack URL: `https://nextwatch-monitoring.grafana.net`

***REMOVED******REMOVED******REMOVED*** 2. Get Grafana Cloud Credentials

In your Grafana Cloud stack:

1. **Metrics (Prometheus)**:

   - Go to **Connections** → **Add new connection** → **Hosted Prometheus metrics**
   - Copy the **Remote Write URL**
   - Generate API token with **MetricsPublisher** role

2. **Logs (Loki)**:
   - Go to **Connections** → **Add new connection** → **Hosted Logs**
   - Copy the **Loki URL**
   - Generate API token with **LogsPublisher** role

***REMOVED******REMOVED******REMOVED*** 3. Configure Environment

```bash
cd infra/monitoring/alloy

***REMOVED*** Copy environment template
cp .env.example .env

***REMOVED*** Edit with your actual credentials
nano .env
```

Fill in your `.env` file:

```bash
GRAFANA_CLOUD_METRICS_URL=https://prometheus-prod-XX-XX-X.grafana.net/api/prom/push
GRAFANA_CLOUD_METRICS_USERNAME=123456
GRAFANA_CLOUD_METRICS_PASSWORD=glc_eyJ...

GRAFANA_CLOUD_LOGS_URL=https://logs-prod-XX-XX-X.grafana.net/loki/api/v1/push
GRAFANA_CLOUD_LOGS_USERNAME=123456
GRAFANA_CLOUD_LOGS_PASSWORD=glc_eyJ...
```

***REMOVED******REMOVED******REMOVED*** 4. Deploy Alloy

```bash
***REMOVED*** Run the setup script
./setup-alloy.sh
```

The script will:

- ✅ Validate credentials
- ✅ Create Docker networks
- ✅ Pull Alloy image
- ✅ Start Alloy container
- ✅ Verify health

***REMOVED******REMOVED******REMOVED*** 5. Verify Setup

1. **Alloy UI**: http://localhost:12345
2. **Check metrics in Grafana Cloud**: Your stack → Explore → Prometheus
3. **Test query**: `up{service="backend-api"}`

***REMOVED******REMOVED*** 📊 What Gets Monitored

***REMOVED******REMOVED******REMOVED*** Phase 1: Critical Services Only (Tier 1)

- **backend-api**: Core business logic
- **bff-api**: Frontend interface
- **auth-api**: Authentication

***REMOVED******REMOVED******REMOVED*** Metrics Collected (Heavily Filtered)

- `up` - Service availability
- `http_requests_total` - Request counts
- `http_request_duration_seconds_*` - Response times
- `health_status` - Health check status
- `process_cpu_seconds_total` - CPU usage
- `process_resident_memory_bytes` - Memory usage

***REMOVED******REMOVED******REMOVED*** Logs Collected (ERROR/WARN Only)

- Container logs for critical services
- Service log files from mounted volumes
- Only ERROR, WARN, FATAL, CRITICAL levels

***REMOVED******REMOVED*** 🔧 Management Commands

```bash
***REMOVED*** View Alloy logs
docker compose -f docker-compose.alloy.yml logs -f grafana-alloy

***REMOVED*** Restart Alloy
docker compose -f docker-compose.alloy.yml restart

***REMOVED*** Stop Alloy
docker compose -f docker-compose.alloy.yml down

***REMOVED*** Update configuration (edit config.alloy then)
docker compose -f docker-compose.alloy.yml restart grafana-alloy
```

***REMOVED******REMOVED*** 📈 Free Tier Usage Monitoring

***REMOVED******REMOVED******REMOVED*** Expected Usage (Tier 1 Only)

- **Metric series**: ~3,000-4,000 (out of 10,000 limit)
- **Logs volume**: ~5-10GB/month (out of 50GB limit)
- **Services**: 3 critical APIs

***REMOVED******REMOVED******REMOVED*** Monitor Usage

1. **Grafana Cloud**: Stack → Usage dashboard
2. **Alloy UI**: http://localhost:12345 → Targets
3. **Query**: `prometheus_tsdb_symbol_table_size_bytes` (metric cardinality)

***REMOVED******REMOVED******REMOVED*** Adding More Services (Phase 2)

Only after validating Tier 1 usage is stable:

1. Edit `config.alloy`
2. Uncomment Tier 2 services section:
   ```hcl
   // Uncomment these blocks for search-api, ml-api, recommendation-api
   ```
3. Restart: `docker-compose -f docker-compose.alloy.yml restart`
4. Monitor usage increase carefully

***REMOVED******REMOVED*** 🚨 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Alloy Not Starting

```bash
***REMOVED*** Check logs
docker-compose -f docker-compose.alloy.yml logs grafana-alloy

***REMOVED*** Common issues:
***REMOVED*** 1. Invalid credentials in .env
***REMOVED*** 2. NextWatch services not running
***REMOVED*** 3. Network conflicts
```

***REMOVED******REMOVED******REMOVED*** No Metrics in Grafana Cloud

```bash
***REMOVED*** Check Alloy targets
curl http://localhost:12345/api/v1/targets

***REMOVED*** Check if NextWatch services are accessible
curl http://backend-api:8000/metrics
```

***REMOVED******REMOVED******REMOVED*** Exceeding Free Tier Limits

```bash
***REMOVED*** Check current usage
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://grafana.com/api/usage/v1/metrics/series"

***REMOVED*** If approaching limits:
***REMOVED*** 1. Increase scraping intervals in config.alloy
***REMOVED*** 2. Add more aggressive metric filtering
***REMOVED*** 3. Remove non-essential services temporarily
```

***REMOVED******REMOVED*** 📁 File Structure

```
alloy/
├── docker-compose.alloy.yml  ***REMOVED*** Docker Compose configuration
├── config.alloy             ***REMOVED*** Alloy configuration (heavily filtered)
├── .env.example             ***REMOVED*** Environment template
├── .env                     ***REMOVED*** Your credentials (create this)
├── setup-alloy.sh           ***REMOVED*** Automated setup script
└── README.md               ***REMOVED*** This file
```

***REMOVED******REMOVED*** 🔄 Integration with Existing Monitoring

This Alloy setup:

- ✅ Uses same Docker networks as current monitoring stack
- ✅ Accesses same service log volumes
- ✅ Replaces Prometheus + Promtail with single agent
- ✅ Maintains existing health monitoring patterns
- ✅ Preserves 3-tier health status system

***REMOVED******REMOVED*** 🎯 Next Steps

1. **Week 1**: Validate Tier 1 services only
2. **Week 2**: Add Tier 2 services if usage allows
3. **Week 3**: Migrate dashboards to Grafana Cloud
4. **Week 4**: Decommission self-hosted Prometheus/Grafana
