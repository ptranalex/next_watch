***REMOVED*** Local Testing Guide: OpenTelemetry Tracing Integration

This guide walks you through testing the OpenTelemetry tracing integration we implemented in `fast-core` and the monitoring configuration locally.

***REMOVED******REMOVED*** 🏗️ Overview

The tracing integration includes:

- **fast-core middleware**: Automatic instrumentation for FastAPI services
- **config service**: Environment configuration for tracing
- **Tempo backend**: Local Tempo instance for trace storage
- **Grafana integration**: Visualization and correlation

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** 1. Start Local Monitoring Stack

```bash
***REMOVED*** Start Tempo + Grafana + Prometheus + Loki locally
./scripts/start-monitoring-with-tempo.sh
```

This will:

- Start all monitoring services in Docker
- Create `.env.tracing` with local configuration
- Set up Grafana data sources
- Enable trace correlation

***REMOVED******REMOVED******REMOVED*** 2. Configure Service for Tracing

Pick one service to test with (e.g., `backend-api`):

```bash
cd apps/backend-api

***REMOVED*** Create environment file for tracing
cat > .env.tracing << EOF
***REMOVED*** Enable distributed tracing
ENABLE_TRACING=true

***REMOVED*** Local Tempo endpoint (gRPC)
TRACING_ENDPOINT=http://localhost:4317

***REMOVED*** High sampling rate for testing (100%)
TRACING_SAMPLE_RATE=1.0

***REMOVED*** Service identification
SERVICE_NAME=backend-api
SERVICE_VERSION=1.0.0
ENVIRONMENT=development
EOF
```

***REMOVED******REMOVED******REMOVED*** 3. Install Dependencies

The OpenTelemetry dependencies were added to `fast-core`:

```bash
***REMOVED*** Make sure you have the latest fast-core with tracing dependencies
cd libs/fast-core
hatch shell
pip install -e .[monitoring]
```

Verify the dependencies are installed:

```bash
pip list | grep opentelemetry
```

Should show:

```
opentelemetry-api              1.20.0
opentelemetry-exporter-otlp    1.20.0
opentelemetry-instrumentation-fastapi 0.41b0
opentelemetry-instrumentation-httpx   0.41b0
opentelemetry-instrumentation-logging 0.41b0
opentelemetry-sdk              1.20.0
```

***REMOVED******REMOVED******REMOVED*** 4. Start Service with Tracing

```bash
cd apps/backend-api

***REMOVED*** Load tracing environment
source .env.tracing

***REMOVED*** Start the service (will automatically pick up tracing config)
hatch shell
python -m uvicorn backend_api.main:create_app --factory --reload --host 0.0.0.0 --port 8001
```

***REMOVED******REMOVED*** 🧪 Testing Scenarios

***REMOVED******REMOVED******REMOVED*** Test 1: Basic Trace Generation

**Make HTTP requests to generate traces:**

```bash
***REMOVED*** Health check (should create simple trace)
curl http://localhost:8001/health

***REMOVED*** API endpoint (should create more complex trace)
curl http://localhost:8001/api/v1/movies

***REMOVED*** Database operation (should show SQL instrumentation)
curl http://localhost:8001/api/v1/movies/1
```

**Expected behavior:**

- Service logs should show trace IDs: `trace_id=abc123...`
- No OpenTelemetry errors in console
- Service starts without tracing-related errors

***REMOVED******REMOVED******REMOVED*** Test 2: Verify Trace Export

**Check Tempo is receiving traces:**

```bash
***REMOVED*** Check Tempo health
curl http://localhost:3200/ready

***REMOVED*** Search for traces (may take 30-60 seconds to appear)
curl "http://localhost:3200/api/search?tags=service.name=backend-api"

***REMOVED*** Check specific trace by ID (get from logs)
curl "http://localhost:3200/api/traces/TRACE_ID_FROM_LOGS"
```

**Expected response:**

```json
{
  "traces": [
    {
      "traceID": "abc123...",
      "spans": [...]
    }
  ]
}
```

***REMOVED******REMOVED******REMOVED*** Test 3: Grafana Visualization

**Open Grafana and test trace queries:**

1. **Access Grafana**: http://localhost:3001 (admin/admin)

2. **Navigate to Explore**: Menu → Explore

3. **Select Tempo data source**: Dropdown at top

4. **Query traces**:

   ```traceql
   ***REMOVED*** Find traces from your service
   {resource.service.name="backend-api"}

   ***REMOVED*** Find slow requests (>100ms)
   {resource.service.name="backend-api" && duration>100ms}

   ***REMOVED*** Find specific HTTP methods
   {span.http.method="GET"}
   ```

5. **Expected results**: Trace timeline showing spans, durations, and service information

***REMOVED******REMOVED******REMOVED*** Test 4: Log-Trace Correlation

**Verify trace IDs appear in logs:**

```bash
***REMOVED*** Make request and check logs
curl http://localhost:8001/api/v1/movies/1

***REMOVED*** Check service logs for trace ID
docker logs backend-api 2>&1 | grep trace_id
```

**Expected log format:**

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Processing movie request",
  "trace_id": "abc123...",
  "span_id": "def456...",
  "movie_id": 1
}
```

***REMOVED******REMOVED******REMOVED*** Test 5: Multi-Service Tracing

**Test trace propagation between services:**

If you have multiple services running:

```bash
***REMOVED*** Start BFF API (which calls backend-api)
cd apps/bff-api
source .env.tracing  ***REMOVED*** Same config
python -m uvicorn bff_api.main:create_app --factory --reload --host 0.0.0.0 --port 8000

***REMOVED*** Make request that spans multiple services
curl http://localhost:8000/bff/v1/movies/1
```

**Expected behavior:**

- Single trace ID spans both services
- Parent-child span relationships
- Service map in Grafana shows connections

***REMOVED******REMOVED*** 🔧 Configuration Testing

***REMOVED******REMOVED******REMOVED*** Test Different Sampling Rates

Edit `.env.tracing` and restart service:

```bash
***REMOVED*** Test low sampling (10%)
TRACING_SAMPLE_RATE=0.1

***REMOVED*** Test high sampling (100% for development)
TRACING_SAMPLE_RATE=1.0

***REMOVED*** Test no tracing
ENABLE_TRACING=false
```

***REMOVED******REMOVED******REMOVED*** Test Configuration Loading

**Create a test script to validate config:**

```python
***REMOVED*** test_tracing_config.py
from config.services.monitoring import MonitoringConfigMixin
from backend_api.config.app import BackendAPIConfig

***REMOVED*** Test configuration loading
config = BackendAPIConfig()
print(f"Tracing enabled: {config.monitoring.enable_tracing}")
print(f"Tracing endpoint: {config.monitoring.tracing_endpoint}")
print(f"Sample rate: {config.monitoring.tracing_sample_rate}")
```

Run with:

```bash
source .env.tracing
python test_tracing_config.py
```

***REMOVED******REMOVED*** 🐛 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Common Issues

***REMOVED******REMOVED******REMOVED******REMOVED*** 1. Service Won't Start with Tracing

**Error**: `ImportError: No module named 'opentelemetry'`

**Solution**:

```bash
cd libs/fast-core
hatch shell
pip install -e .[monitoring]
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 2. No Traces in Tempo

**Check**:

```bash
***REMOVED*** Verify Tempo is running
docker ps | grep tempo

***REMOVED*** Check Tempo logs
docker logs tempo-prod

***REMOVED*** Verify endpoint connectivity
telnet localhost 4317
```

**Common causes**:

- Tempo not running (run monitoring script)
- Wrong endpoint in `.env.tracing`
- Service not configured for tracing

***REMOVED******REMOVED******REMOVED******REMOVED*** 3. Traces Not Appearing in Grafana

**Check**:

```bash
***REMOVED*** Verify Grafana data source
curl http://admin:admin@localhost:3001/api/datasources

***REMOVED*** Check if Tempo data source is configured
curl http://admin:admin@localhost:3001/api/datasources | grep tempo
```

**Fix**: Re-run monitoring script to reconfigure data sources

***REMOVED******REMOVED******REMOVED******REMOVED*** 4. Missing Trace IDs in Logs

**Verify logging instrumentation**:

```python
***REMOVED*** Check if logging is instrumented
import logging
from opentelemetry.instrumentation.logging import LoggingInstrumentor

***REMOVED*** Should be called in fast-core middleware
LoggingInstrumentor().instrument()
```

***REMOVED******REMOVED******REMOVED*** Debug Commands

**Check OpenTelemetry configuration:**

```bash
***REMOVED*** Environment variables
env | grep -i tracing

***REMOVED*** Check if tracer is configured
python -c "from opentelemetry import trace; print(trace.get_tracer_provider())"
```

**Monitor trace export:**

```bash
***REMOVED*** Tempo metrics
curl http://localhost:3200/metrics | grep -i traces

***REMOVED*** Service metrics (if Prometheus enabled)
curl http://localhost:8001/metrics | grep -i trace
```

***REMOVED******REMOVED*** 📊 Validation Checklist

After running tests, verify:

- [ ] **Service Startup**: Service starts without OpenTelemetry errors
- [ ] **Trace Generation**: HTTP requests generate traces with proper IDs
- [ ] **Trace Export**: Traces appear in Tempo within 60 seconds
- [ ] **Grafana Integration**: Traces visible in Grafana Explore
- [ ] **Log Correlation**: Trace IDs appear in structured logs
- [ ] **Instrumentation**: Database and HTTP calls are instrumented
- [ ] **Configuration**: Environment variables control tracing behavior

***REMOVED******REMOVED*** 🎯 Expected Performance Impact

**Resource Usage (with 100% sampling)**:

- **CPU**: +2-5% overhead
- **Memory**: +50-100MB per service
- **Network**: ~5-10KB per trace

**In production, use 1-10% sampling to minimize impact**

***REMOVED******REMOVED*** 🔄 Continuous Testing

**Add to your development workflow:**

```bash
***REMOVED*** Before committing changes
make test-tracing

***REMOVED*** In CI/CD pipeline
docker compose -f infra/compose/monitoring.yml up -d
./scripts/test-tracing-integration.sh
```

This ensures tracing doesn't break with code changes.

***REMOVED******REMOVED*** 📚 Next Steps

Once local testing works:

1. **Deploy to staging** with 10% sampling
2. **Test cross-service traces** in full environment
3. **Set up alerts** for trace ingestion failures
4. **Train team** on using Grafana for troubleshooting
5. **Document trace analysis workflows**

***REMOVED******REMOVED*** 🎉 Success Criteria

Your tracing integration is working when:

- ✅ Services start and run normally with tracing enabled
- ✅ Every HTTP request generates a trace visible in Grafana
- ✅ Traces show database queries, HTTP calls, and service boundaries
- ✅ Log entries include trace IDs for correlation
- ✅ Multi-service requests show connected traces
- ✅ Performance impact is minimal (<5% CPU overhead)

Now you have distributed tracing working locally and can start using it for debugging and performance analysis!
