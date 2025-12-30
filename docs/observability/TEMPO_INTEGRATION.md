# Grafana Tempo Integration for Distributed Tracing

This document outlines how to integrate and use Grafana Tempo for distributed tracing across NextWatch services.

## Overview

Grafana Tempo is a high-scale distributed tracing backend that integrates seamlessly with Grafana, Prometheus, and Loki. Our implementation uses OpenTelemetry to send traces to Tempo, enabling full observability correlation between metrics, logs, and traces.

## Architecture

```
FastAPI Services → OpenTelemetry → Tempo → Grafana
                ↗ Prometheus (metrics with exemplars)
               ↗ Loki (logs with trace IDs)
```

### Key Components

- **OpenTelemetry**: Instrumentation and trace collection
- **Tempo**: Trace storage and querying backend
- **Grafana**: Visualization and correlation UI
- **Prometheus**: Metrics with trace exemplars
- **Loki**: Logs with trace ID correlation

## Configuration

### Tempo Configuration (v2.6+)

The Tempo configuration has been updated for compatibility with version 2.6:

```yaml
# tempo.yml
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

compactor:
  compaction:
    block_retention: 24h # Note: retention_duration removed in 2.6+
    compaction_window: 1h

query_frontend: # Note: query_timeout moved here in 2.6+
  search:
    query_timeout: 30s
  trace_by_id:
    query_timeout: 10s

overrides: # Note: uses 'defaults' block in 2.6+
  defaults:
    metrics_generator:
      processors:
        - service-graphs
        - span-metrics
        - local-blocks
```

### Important Configuration Changes in Tempo 2.6

1. **Compactor Changes**:

   - `retention_duration` → `block_retention`
   - Moved from compactor level to compaction block

2. **Query Configuration**:

   - `query_timeout` moved from querier to query_frontend
   - Separate timeouts for search vs trace_by_id

3. **Overrides Schema**:
   - Now uses `defaults` block structure
   - Updated metrics_generator configuration

### Grafana Data Sources

Configured with correlation between data sources:

```yaml
# prometheus.yml
datasources:
  - name: Tempo
    type: tempo
    uid: tempo
    url: http://tempo:3200

  - name: Loki
    type: loki
    uid: loki
    url: http://loki:3100
    jsonData:
      derivedFields:
        - datasourceUid: tempo
          matcherRegex: "trace_id=([a-f0-9]+)"
          name: TraceID
          url: "$${__value.raw}"
```

## OpenTelemetry Integration

### FastAPI Services Setup

Each service uses the fast-core tracing middleware:

```python
# In fast-core middleware
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def setup_tracing(app: FastAPI, settings):
    if not settings.monitoring.enable_tracing:
        return

    # Configure resource
    resource = Resource.create({
        "service.name": settings.service_name,
        "service.version": settings.service_version,
        "environment": settings.environment
    })

    # Set up OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.monitoring.tracing_endpoint,
        insecure=True
    )

    # Configure tracer provider
    tracer_provider = TracerProvider(
        resource=resource,
        sampler=TraceIdRatioBasedSampler(settings.monitoring.tracing_sample_rate)
    )

    # Set up span processor
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Set global tracer provider
    trace.set_tracer_provider(tracer_provider)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
```

### Environment Configuration

```bash
# .env.tracing
TEMPO_ENDPOINT=http://localhost:4317
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=0.1  # 10% sampling for production
```

## Features

### TraceQL Support

Tempo 2.6 includes enhanced TraceQL support:

```traceql
# Find slow HTTP requests
{ span.http.method = "POST" && duration > 1s }

# Find errors in specific service
{ resource.service.name = "backend-api" && status = error }

# Find traces with specific attributes
{ span.db.operation = "SELECT" && resource.environment = "production" }
```

### Metrics Integration

- **Service Graphs**: Automatic service topology mapping
- **Span Metrics**: RED (Rate, Errors, Duration) metrics from traces
- **Exemplars**: Link from Prometheus metrics to traces

### Log Correlation

Logs automatically include trace IDs for correlation:

```python
# Structured logging with trace context
logger.info(
    "Processing request",
    extra={
        "trace_id": trace_context.trace_id,
        "span_id": trace_context.span_id,
        "user_id": user.id
    }
)
```

## Deployment

### Docker Compose

```yaml
# infra/compose/monitoring.yml
tempo:
  image: grafana/tempo:2.6.0
  ports:
    - "3200:3200" # HTTP API
    - "4317:4317" # OTLP gRPC
    - "4318:4318" # OTLP HTTP
  volumes:
    - ./monitoring/tempo/tempo.yml:/etc/tempo.yaml
```

### Production Considerations

1. **Storage**: Use object storage (S3, GCS, Azure) for production
2. **Scaling**: Deploy distributors, ingesters, and queriers separately
3. **Retention**: Configure appropriate trace retention periods
4. **Sampling**: Adjust sampling rates based on volume
5. **Security**: Enable authentication and TLS

## Troubleshooting

### Common Issues

#### Configuration Parsing Errors

**Problem**:

```
failed parsing config: field retention_duration not found in type tempodb.CompactorConfig
```

**Solution**: Update to Tempo 2.6+ configuration format:

```yaml
# OLD (2.5 and earlier)
compactor:
  compaction:
    retention_duration: 24h

# NEW (2.6+)
compactor:
  compaction:
    block_retention: 24h
```

#### Query Timeout Errors

**Problem**: `query_timeout not found in type querier.Config`

**Solution**: Move timeout configuration to query_frontend:

```yaml
# OLD
querier:
  query_timeout: 30s

# NEW
query_frontend:
  search:
    query_timeout: 30s
  trace_by_id:
    query_timeout: 10s
```

#### Overrides Configuration

**Problem**: `defaults not found in type overrides.legacyConfig`

**Solution**: Use correct overrides schema:

```yaml
# NEW format for 2.6+
overrides:
  defaults:
    metrics_generator:
      processors: [service-graphs, span-metrics, local-blocks]
```

### Monitoring Tempo

Key metrics to monitor:

```yaml
# Ingestion rate
tempo_distributor_ingester_appends_total

# Query performance
tempo_query_frontend_queries_total
tempo_query_frontend_query_duration_seconds

# Storage health
tempo_ingester_blocks_flushed_total
tempo_compactor_blocks_processed_total
```

### Performance Tuning

1. **Sampling**: Start with 1% sampling, adjust based on volume
2. **Batch Processing**: Configure appropriate batch sizes
3. **Memory**: Ensure adequate memory for ingester components
4. **Network**: Monitor network bandwidth for OTLP traffic

## Usage Examples

### Viewing Traces in Grafana

1. Navigate to Grafana → Explore
2. Select Tempo data source
3. Enter trace ID or use TraceQL query
4. Explore correlated logs and metrics

### Trace Analysis

- **Service Dependencies**: Use service graph view
- **Performance Bottlenecks**: Analyze span durations
- **Error Investigation**: Filter by status = error
- **Resource Usage**: Correlate with Prometheus metrics

### API Access

```bash
# Query traces by ID
curl "http://tempo:3200/api/traces/TRACE_ID"

# Search traces
curl "http://tempo:3200/api/search?tags=service.name=backend-api"

# TraceQL query
curl -G "http://tempo:3200/api/search" \
  --data-urlencode 'q={duration>1s}'
```

## Best Practices

1. **Instrumentation**: Instrument at service boundaries
2. **Attributes**: Add meaningful span attributes
3. **Sampling**: Use adaptive sampling strategies
4. **Storage**: Plan for storage growth with retention policies
5. **Security**: Secure OTLP endpoints in production
6. **Monitoring**: Monitor Tempo's own performance metrics

## References

- [Tempo Configuration Documentation](https://grafana.com/docs/tempo/latest/configuration/)
- [OpenTelemetry Python Documentation](https://opentelemetry-python.readthedocs.io/)
- [TraceQL Query Language](https://grafana.com/docs/tempo/latest/traceql/)
- [Tempo 2.6 Release Notes](https://grafana.com/docs/tempo/latest/release-notes/v2-6/)
