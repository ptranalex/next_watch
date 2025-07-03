***REMOVED*** Grafana Tempo Integration for Distributed Tracing

This document outlines how to integrate and use Grafana Tempo for distributed tracing across NextWatch services.

***REMOVED******REMOVED*** Overview

Grafana Tempo is a high-scale distributed tracing backend that integrates seamlessly with Grafana, Prometheus, and Loki. Our implementation uses OpenTelemetry to send traces to Tempo, enabling full observability correlation between metrics, logs, and traces.

***REMOVED******REMOVED*** Architecture

```
FastAPI Services → OpenTelemetry → Tempo → Grafana
                ↗ Prometheus (metrics with exemplars)
               ↗ Loki (logs with trace IDs)
```

***REMOVED******REMOVED******REMOVED*** Key Components

- **OpenTelemetry**: Instrumentation and trace collection
- **Tempo**: Trace storage and querying backend
- **Grafana**: Visualization and correlation UI
- **Prometheus**: Metrics with trace exemplars
- **Loki**: Logs with trace ID correlation

***REMOVED******REMOVED*** Configuration

***REMOVED******REMOVED******REMOVED*** Tempo Configuration (v2.6+)

The Tempo configuration has been updated for compatibility with version 2.6:

```yaml
***REMOVED*** tempo.yml
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
    block_retention: 24h ***REMOVED*** Note: retention_duration removed in 2.6+
    compaction_window: 1h

query_frontend: ***REMOVED*** Note: query_timeout moved here in 2.6+
  search:
    query_timeout: 30s
  trace_by_id:
    query_timeout: 10s

overrides: ***REMOVED*** Note: uses 'defaults' block in 2.6+
  defaults:
    metrics_generator:
      processors:
        - service-graphs
        - span-metrics
        - local-blocks
```

***REMOVED******REMOVED******REMOVED*** Important Configuration Changes in Tempo 2.6

1. **Compactor Changes**:

   - `retention_duration` → `block_retention`
   - Moved from compactor level to compaction block

2. **Query Configuration**:

   - `query_timeout` moved from querier to query_frontend
   - Separate timeouts for search vs trace_by_id

3. **Overrides Schema**:
   - Now uses `defaults` block structure
   - Updated metrics_generator configuration

***REMOVED******REMOVED******REMOVED*** Grafana Data Sources

Configured with correlation between data sources:

```yaml
***REMOVED*** prometheus.yml
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

***REMOVED******REMOVED*** OpenTelemetry Integration

***REMOVED******REMOVED******REMOVED*** FastAPI Services Setup

Each service uses the fast-core tracing middleware:

```python
***REMOVED*** In fast-core middleware
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def setup_tracing(app: FastAPI, settings):
    if not settings.monitoring.enable_tracing:
        return

    ***REMOVED*** Configure resource
    resource = Resource.create({
        "service.name": settings.service_name,
        "service.version": settings.service_version,
        "environment": settings.environment
    })

    ***REMOVED*** Set up OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.monitoring.tracing_endpoint,
        insecure=True
    )

    ***REMOVED*** Configure tracer provider
    tracer_provider = TracerProvider(
        resource=resource,
        sampler=TraceIdRatioBasedSampler(settings.monitoring.tracing_sample_rate)
    )

    ***REMOVED*** Set up span processor
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    ***REMOVED*** Set global tracer provider
    trace.set_tracer_provider(tracer_provider)

    ***REMOVED*** Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
```

***REMOVED******REMOVED******REMOVED*** Environment Configuration

```bash
***REMOVED*** .env.tracing
TEMPO_ENDPOINT=http://localhost:4317
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=0.1  ***REMOVED*** 10% sampling for production
```

***REMOVED******REMOVED*** Features

***REMOVED******REMOVED******REMOVED*** TraceQL Support

Tempo 2.6 includes enhanced TraceQL support:

```traceql
***REMOVED*** Find slow HTTP requests
{ span.http.method = "POST" && duration > 1s }

***REMOVED*** Find errors in specific service
{ resource.service.name = "backend-api" && status = error }

***REMOVED*** Find traces with specific attributes
{ span.db.operation = "SELECT" && resource.environment = "production" }
```

***REMOVED******REMOVED******REMOVED*** Metrics Integration

- **Service Graphs**: Automatic service topology mapping
- **Span Metrics**: RED (Rate, Errors, Duration) metrics from traces
- **Exemplars**: Link from Prometheus metrics to traces

***REMOVED******REMOVED******REMOVED*** Log Correlation

Logs automatically include trace IDs for correlation:

```python
***REMOVED*** Structured logging with trace context
logger.info(
    "Processing request",
    extra={
        "trace_id": trace_context.trace_id,
        "span_id": trace_context.span_id,
        "user_id": user.id
    }
)
```

***REMOVED******REMOVED*** Deployment

***REMOVED******REMOVED******REMOVED*** Docker Compose

```yaml
***REMOVED*** docker-compose.monitoring.yml
tempo:
  image: grafana/tempo:2.6.0
  ports:
    - "3200:3200" ***REMOVED*** HTTP API
    - "4317:4317" ***REMOVED*** OTLP gRPC
    - "4318:4318" ***REMOVED*** OTLP HTTP
  volumes:
    - ./monitoring/tempo/tempo.yml:/etc/tempo.yaml
```

***REMOVED******REMOVED******REMOVED*** Production Considerations

1. **Storage**: Use object storage (S3, GCS, Azure) for production
2. **Scaling**: Deploy distributors, ingesters, and queriers separately
3. **Retention**: Configure appropriate trace retention periods
4. **Sampling**: Adjust sampling rates based on volume
5. **Security**: Enable authentication and TLS

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Common Issues

***REMOVED******REMOVED******REMOVED******REMOVED*** Configuration Parsing Errors

**Problem**:

```
failed parsing config: field retention_duration not found in type tempodb.CompactorConfig
```

**Solution**: Update to Tempo 2.6+ configuration format:

```yaml
***REMOVED*** OLD (2.5 and earlier)
compactor:
  compaction:
    retention_duration: 24h

***REMOVED*** NEW (2.6+)
compactor:
  compaction:
    block_retention: 24h
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Query Timeout Errors

**Problem**: `query_timeout not found in type querier.Config`

**Solution**: Move timeout configuration to query_frontend:

```yaml
***REMOVED*** OLD
querier:
  query_timeout: 30s

***REMOVED*** NEW
query_frontend:
  search:
    query_timeout: 30s
  trace_by_id:
    query_timeout: 10s
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Overrides Configuration

**Problem**: `defaults not found in type overrides.legacyConfig`

**Solution**: Use correct overrides schema:

```yaml
***REMOVED*** NEW format for 2.6+
overrides:
  defaults:
    metrics_generator:
      processors: [service-graphs, span-metrics, local-blocks]
```

***REMOVED******REMOVED******REMOVED*** Monitoring Tempo

Key metrics to monitor:

```yaml
***REMOVED*** Ingestion rate
tempo_distributor_ingester_appends_total

***REMOVED*** Query performance
tempo_query_frontend_queries_total
tempo_query_frontend_query_duration_seconds

***REMOVED*** Storage health
tempo_ingester_blocks_flushed_total
tempo_compactor_blocks_processed_total
```

***REMOVED******REMOVED******REMOVED*** Performance Tuning

1. **Sampling**: Start with 1% sampling, adjust based on volume
2. **Batch Processing**: Configure appropriate batch sizes
3. **Memory**: Ensure adequate memory for ingester components
4. **Network**: Monitor network bandwidth for OTLP traffic

***REMOVED******REMOVED*** Usage Examples

***REMOVED******REMOVED******REMOVED*** Viewing Traces in Grafana

1. Navigate to Grafana → Explore
2. Select Tempo data source
3. Enter trace ID or use TraceQL query
4. Explore correlated logs and metrics

***REMOVED******REMOVED******REMOVED*** Trace Analysis

- **Service Dependencies**: Use service graph view
- **Performance Bottlenecks**: Analyze span durations
- **Error Investigation**: Filter by status = error
- **Resource Usage**: Correlate with Prometheus metrics

***REMOVED******REMOVED******REMOVED*** API Access

```bash
***REMOVED*** Query traces by ID
curl "http://tempo:3200/api/traces/TRACE_ID"

***REMOVED*** Search traces
curl "http://tempo:3200/api/search?tags=service.name=backend-api"

***REMOVED*** TraceQL query
curl -G "http://tempo:3200/api/search" \
  --data-urlencode 'q={duration>1s}'
```

***REMOVED******REMOVED*** Best Practices

1. **Instrumentation**: Instrument at service boundaries
2. **Attributes**: Add meaningful span attributes
3. **Sampling**: Use adaptive sampling strategies
4. **Storage**: Plan for storage growth with retention policies
5. **Security**: Secure OTLP endpoints in production
6. **Monitoring**: Monitor Tempo's own performance metrics

***REMOVED******REMOVED*** References

- [Tempo Configuration Documentation](https://grafana.com/docs/tempo/latest/configuration/)
- [OpenTelemetry Python Documentation](https://opentelemetry-python.readthedocs.io/)
- [TraceQL Query Language](https://grafana.com/docs/tempo/latest/traceql/)
- [Tempo 2.6 Release Notes](https://grafana.com/docs/tempo/latest/release-notes/v2-6/)
