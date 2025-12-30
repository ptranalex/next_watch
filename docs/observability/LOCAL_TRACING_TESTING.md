# Local Testing Guide: OpenTelemetry Tracing Integration

This guide walks you through testing the OpenTelemetry tracing integration we implemented in `fast-core` and the monitoring configuration locally.

## 🏗️ Overview

The tracing integration includes:

- **fast-core middleware**: Automatic instrumentation for FastAPI services
- **config service**: Environment configuration for tracing
- **Tempo backend**: Local Tempo instance for trace storage
- **Grafana integration**: Visualization and correlation

## 🚀 Quick Start

### 1. Start Local Monitoring Stack

```bash
# Start Tempo + Grafana + Prometheus + Loki locally
./scripts/start-monitoring-with-tempo.sh
```

This will:

- Start all monitoring services in Docker
- Create `.env.tracing` with local configuration
- Set up Grafana data sources
- Enable trace correlation

### 2. Configure Service for Tracing

Pick one service to test with (e.g., `backend-api`):

```bash
cd apps/backend-api

# Create environment file for tracing
cat > .env.tracing << EOF
# Enable distributed tracing
ENABLE_TRACING=true

# Local Tempo endpoint (gRPC)
TRACING_ENDPOINT=http://localhost:4317

# High sampling rate for testing (100%)
TRACING_SAMPLE_RATE=1.0

# Service identification
SERVICE_NAME=backend-api
SERVICE_VERSION=1.0.0
ENVIRONMENT=development
EOF
```

### 3. Install Dependencies

The OpenTelemetry dependencies were added to `fast-core`:

```bash
# Make sure you have the latest fast-core with tracing dependencies
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

### 4. Start Service with Tracing

```bash
cd apps/backend-api

# Load tracing environment
source .env.tracing

# Start the service (will automatically pick up tracing config)
hatch shell
python -m uvicorn backend_api.main:create_app --factory --reload --host 0.0.0.0 --port 8001
```

## 🧪 Testing Scenarios

### Test 1: Basic Trace Generation

**Make HTTP requests to generate traces:**

```bash
# Health check (should create simple trace)
curl http://localhost:8001/health

# API endpoint (should create more complex trace)
curl http://localhost:8001/api/v1/movies

# Database operation (should show SQL instrumentation)
curl http://localhost:8001/api/v1/movies/1
```

**Expected behavior:**

- Service logs should show trace IDs: `trace_id=abc123...`
- No OpenTelemetry errors in console
- Service starts without tracing-related errors

### Test 2: Verify Trace Export

**Check Tempo is receiving traces:**

```bash
# Check Tempo health
curl http://localhost:3200/ready

# Search for traces (may take 30-60 seconds to appear)
curl "http://localhost:3200/api/search?tags=service.name=backend-api"

# Check specific trace by ID (get from logs)
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

### Test 3: Grafana Visualization

**Open Grafana and test trace queries:**

1. **Access Grafana**: http://localhost:3001 (admin/admin)

2. **Navigate to Explore**: Menu → Explore

3. **Select Tempo data source**: Dropdown at top

4. **Query traces**:

   ```traceql
   # Find traces from your service
   {resource.service.name="backend-api"}

   # Find slow requests (>100ms)
   {resource.service.name="backend-api" && duration>100ms}

   # Find specific HTTP methods
   {span.http.method="GET"}
   ```

5. **Expected results**: Trace timeline showing spans, durations, and service information

### Test 4: Log-Trace Correlation

**Verify trace IDs appear in logs:**

```bash
# Make request and check logs
curl http://localhost:8001/api/v1/movies/1

# Check service logs for trace ID
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

### Test 5: Multi-Service Tracing

**Test trace propagation between services:**

If you have multiple services running:

```bash
# Start BFF API (which calls backend-api)
cd apps/bff-api
source .env.tracing  # Same config
python -m uvicorn bff_api.main:create_app --factory --reload --host 0.0.0.0 --port 8000

# Make request that spans multiple services
curl http://localhost:8000/bff/v1/movies/1
```

**Expected behavior:**

- Single trace ID spans both services
- Parent-child span relationships
- Service map in Grafana shows connections

## 🔧 Configuration Testing

### Test Different Sampling Rates

Edit `.env.tracing` and restart service:

```bash
# Test low sampling (10%)
TRACING_SAMPLE_RATE=0.1

# Test high sampling (100% for development)
TRACING_SAMPLE_RATE=1.0

# Test no tracing
ENABLE_TRACING=false
```

### Test Configuration Loading

**Create a test script to validate config:**

```python
# test_tracing_config.py
from config.services.monitoring import MonitoringConfigMixin
from backend_api.config.app import BackendAPIConfig

# Test configuration loading
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

## 🐛 Troubleshooting

### Common Issues

#### 1. Service Won't Start with Tracing

**Error**: `ImportError: No module named 'opentelemetry'`

**Solution**:

```bash
cd libs/fast-core
hatch shell
pip install -e .[monitoring]
```

#### 2. No Traces in Tempo

**Check**:

```bash
# Verify Tempo is running
docker ps | grep tempo

# Check Tempo logs
docker logs tempo-prod

# Verify endpoint connectivity
telnet localhost 4317
```

**Common causes**:

- Tempo not running (run monitoring script)
- Wrong endpoint in `.env.tracing`
- Service not configured for tracing

#### 3. Traces Not Appearing in Grafana

**Check**:

```bash
# Verify Grafana data source
curl http://admin:admin@localhost:3001/api/datasources

# Check if Tempo data source is configured
curl http://admin:admin@localhost:3001/api/datasources | grep tempo
```

**Fix**: Re-run monitoring script to reconfigure data sources

#### 4. Missing Trace IDs in Logs

**Verify logging instrumentation**:

```python
# Check if logging is instrumented
import logging
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Should be called in fast-core middleware
LoggingInstrumentor().instrument()
```

### Debug Commands

**Check OpenTelemetry configuration:**

```bash
# Environment variables
env | grep -i tracing

# Check if tracer is configured
python -c "from opentelemetry import trace; print(trace.get_tracer_provider())"
```

**Monitor trace export:**

```bash
# Tempo metrics
curl http://localhost:3200/metrics | grep -i traces

# Service metrics (if Prometheus enabled)
curl http://localhost:8001/metrics | grep -i trace
```

## 📊 Validation Checklist

After running tests, verify:

- [ ] **Service Startup**: Service starts without OpenTelemetry errors
- [ ] **Trace Generation**: HTTP requests generate traces with proper IDs
- [ ] **Trace Export**: Traces appear in Tempo within 60 seconds
- [ ] **Grafana Integration**: Traces visible in Grafana Explore
- [ ] **Log Correlation**: Trace IDs appear in structured logs
- [ ] **Instrumentation**: Database and HTTP calls are instrumented
- [ ] **Configuration**: Environment variables control tracing behavior

## 🎯 Expected Performance Impact

**Resource Usage (with 100% sampling)**:

- **CPU**: +2-5% overhead
- **Memory**: +50-100MB per service
- **Network**: ~5-10KB per trace

**In production, use 1-10% sampling to minimize impact**

## 🔄 Continuous Testing

**Add to your development workflow:**

```bash
# Before committing changes
make test-tracing

# In CI/CD pipeline
docker compose -f infra/compose/monitoring.yml up -d
./scripts/test-tracing-integration.sh
```

This ensures tracing doesn't break with code changes.

## 📚 Next Steps

Once local testing works:

1. **Deploy to staging** with 10% sampling
2. **Test cross-service traces** in full environment
3. **Set up alerts** for trace ingestion failures
4. **Train team** on using Grafana for troubleshooting
5. **Document trace analysis workflows**

## 🎉 Success Criteria

Your tracing integration is working when:

- ✅ Services start and run normally with tracing enabled
- ✅ Every HTTP request generates a trace visible in Grafana
- ✅ Traces show database queries, HTTP calls, and service boundaries
- ✅ Log entries include trace IDs for correlation
- ✅ Multi-service requests show connected traces
- ✅ Performance impact is minimal (<5% CPU overhead)

Now you have distributed tracing working locally and can start using it for debugging and performance analysis!
