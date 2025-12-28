***REMOVED*** Tracing Best Practices Guide

This document outlines when and how to enable distributed tracing across different environments.

***REMOVED******REMOVED*** 🎯 Core Principle

**Enable tracing strategically based on environment and needs, not universally.**

***REMOVED******REMOVED*** 📊 Environment-Specific Configuration

***REMOVED******REMOVED******REMOVED*** 🛠️ Development Environment

**Purpose**: Full visibility for debugging and feature development

```bash
***REMOVED*** Example (dev): infra/env/development.example or per-service .env/.env.local
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=1.0          ***REMOVED*** 100% sampling
TRACING_ENDPOINT=http://localhost:4317
```

**Why 100% sampling in development:**

- Debug every request during development
- Understand full request flow
- Performance impact acceptable with low traffic
- Complete trace coverage for testing

***REMOVED******REMOVED******REMOVED*** 🧪 Staging/Testing Environment

**Purpose**: Validate tracing works before production + performance testing

```bash
***REMOVED*** .env.staging
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=0.3          ***REMOVED*** 30% sampling
TRACING_ENDPOINT=http://tempo-staging:4317
```

**Why 30% sampling in staging:**

- Test tracing at realistic volumes
- Validate trace correlation across services
- Performance testing with tracing overhead
- Catch tracing-related issues before production

***REMOVED******REMOVED******REMOVED*** 🚀 Production Environment

**Purpose**: Essential observability with minimal performance impact

```bash
***REMOVED*** Production env (Docker Compose): .env.prod
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=0.05         ***REMOVED*** 5% sampling
TRACING_ENDPOINT=http://tempo-prod:4317
```

**Why 5% sampling in production:**

- Capture representative request patterns
- Minimize performance and cost impact
- Still get valuable debugging information
- Can increase temporarily for incident investigation

***REMOVED******REMOVED*** 🔧 Configuration Strategies

***REMOVED******REMOVED******REMOVED*** Strategy 1: Environment Variables (Recommended)

```bash
***REMOVED*** Service automatically picks up configuration
export ENABLE_TRACING=true
export TRACING_SAMPLE_RATE=0.1

***REMOVED*** Start service - tracing configured automatically
python -m uvicorn app:create_app --factory
```

***REMOVED******REMOVED******REMOVED*** Strategy 2: Service-Specific Configuration

```yaml
***REMOVED*** Docker Compose (example)
services:
  backend-api:
    environment:
      ENABLE_TRACING: "true"
      TRACING_SAMPLE_RATE: "0.1"

  user-facing-bff:
    environment:
      ENABLE_TRACING: "true"
      TRACING_SAMPLE_RATE: "0.2" ***REMOVED*** Higher sampling for user-facing service

  internal-ml-api:
    environment:
      ENABLE_TRACING: "true"
      TRACING_SAMPLE_RATE: "0.02" ***REMOVED*** Lower sampling for high-volume service
```

***REMOVED******REMOVED******REMOVED*** Strategy 3: Dynamic Configuration

```python
***REMOVED*** For advanced use cases - adaptive sampling
class AdaptiveSampling:
    def get_sample_rate(self, endpoint: str, load: float) -> float:
        if endpoint.startswith("/health"):
            return 0.01  ***REMOVED*** Low sampling for health checks
        elif endpoint.startswith("/api/critical"):
            return 0.5   ***REMOVED*** High sampling for critical endpoints
        elif load > 0.8:
            return 0.02  ***REMOVED*** Reduce sampling under high load
        else:
            return 0.1   ***REMOVED*** Default sampling
```

***REMOVED******REMOVED*** 🎯 When to Enable/Disable Tracing

***REMOVED******REMOVED******REMOVED*** ✅ Always Enable Tracing When:

1. **New Service Development**: Full visibility into request flow
2. **Debugging Production Issues**: Increase sampling temporarily
3. **Performance Analysis**: Understand latency bottlenecks
4. **Service Integration**: Validate cross-service communication
5. **Compliance Requirements**: Some regulations require audit trails

***REMOVED******REMOVED******REMOVED*** ⚠️ Consider Disabling When:

1. **Emergency Performance Issues**: Temporary disable to reduce overhead
2. **High-Volume Batch Jobs**: May not need request-level tracing
3. **Cost Constraints**: Very high traffic with limited observability budget
4. **Privacy-Sensitive Services**: Some traces may contain PII

***REMOVED******REMOVED******REMOVED*** 🔄 Temporarily Increase Sampling When:

```bash
***REMOVED*** Incident investigation
export TRACING_SAMPLE_RATE=1.0  ***REMOVED*** Temporary 100%

***REMOVED*** Performance debugging
export TRACING_SAMPLE_RATE=0.5  ***REMOVED*** Temporary 50%

***REMOVED*** Feature rollout validation
export TRACING_SAMPLE_RATE=0.3  ***REMOVED*** Temporary 30%
```

***REMOVED******REMOVED*** 📈 Sampling Rate Guidelines

***REMOVED******REMOVED******REMOVED*** Traffic Volume Based

```yaml
Request Volume Guide:
  < 1K requests/day:    100% sampling (no impact)
  1K - 10K requests/day: 50% sampling
  10K - 100K requests/day: 10% sampling
  100K - 1M requests/day: 5% sampling
  > 1M requests/day:     1-2% sampling
```

***REMOVED******REMOVED******REMOVED*** Service Type Based

```yaml
Service Type Recommendations:
  User-facing APIs: 10-20% (need good coverage)
  Internal APIs: 5-10% (moderate coverage)
  Background workers: 1-5% (basic coverage)
  Health checks: 0.1% (minimal coverage)
  ML inference: 2-5% (performance sensitive)
```

***REMOVED******REMOVED*** 🔍 Advanced Configuration

***REMOVED******REMOVED******REMOVED*** Head-Based Sampling (Current Implementation)

```python
***REMOVED*** What we implemented - decides at request start
TRACING_SAMPLE_RATE=0.1  ***REMOVED*** 10% of all requests traced end-to-end
```

**Pros**: Simple, predictable resource usage
**Cons**: May miss important traces (errors, slow requests)

***REMOVED******REMOVED******REMOVED*** Tail-Based Sampling (Future Enhancement)

```python
***REMOVED*** Advanced - decides after request completes
sample_if:
  - error_occurred: true
  - duration > 1000ms
  - contains_keyword: "payment"
  - random_sample: 0.05
```

**Pros**: Intelligent sampling, catch all errors
**Cons**: More complex, requires buffering

***REMOVED******REMOVED*** 🚨 Emergency Controls

***REMOVED******REMOVED******REMOVED*** Quick Disable (Emergency)

```bash
***REMOVED*** Fastest way to disable tracing
export ENABLE_TRACING=false

***REMOVED*** Or reduce to minimum
export TRACING_SAMPLE_RATE=0.001  ***REMOVED*** 0.1%
```

***REMOVED******REMOVED******REMOVED*** Service Restart Required

After changing tracing configuration, services need restart:

```bash
***REMOVED*** Graceful restart with new config
docker compose -f infra/compose/prod.yml --env-file .env.prod restart backend-api

***REMOVED*** Or for development
pkill -f uvicorn  ***REMOVED*** Kill and restart manually
```

***REMOVED******REMOVED*** 📊 Monitoring Tracing Health

***REMOVED******REMOVED******REMOVED*** Key Metrics to Monitor

```yaml
Tracing Health Metrics:
  - trace_export_errors_total
  - trace_export_duration_seconds
  - traces_received_total
  - traces_dropped_total
  - tempo_ingester_traces_received_total
```

***REMOVED******REMOVED******REMOVED*** Alerts to Set Up

```yaml
Critical Alerts:
  - Trace export failure rate > 5%
  - Tempo ingestion stopped
  - High trace export latency (>30s)

Warning Alerts:
  - Sampling rate changed
  - Trace volume spike (>2x normal)
  - Missing traces from key services
```

***REMOVED******REMOVED*** 🎯 Team Guidelines

***REMOVED******REMOVED******REMOVED*** Developer Workflow

```bash
***REMOVED*** Starting development work
./scripts/start-monitoring-with-tempo.sh  ***REMOVED*** Start observability stack
./scripts/start-backend-with-tracing.sh   ***REMOVED*** Start service with tracing

***REMOVED*** During debugging
export TRACING_SAMPLE_RATE=1.0  ***REMOVED*** Increase sampling temporarily

***REMOVED*** Before committing
./scripts/test-tracing-integration.sh  ***REMOVED*** Validate tracing works
```

***REMOVED******REMOVED******REMOVED*** Operations Workflow

```bash
***REMOVED*** Production deployment
docker compose -f infra/compose/prod.yml --env-file .env.prod up -d

***REMOVED*** Incident investigation
kubectl set env deployment/backend-api TRACING_SAMPLE_RATE=0.5

***REMOVED*** Performance optimization
kubectl set env deployment/ml-api TRACING_SAMPLE_RATE=0.01
```

***REMOVED******REMOVED*** 🏆 Success Metrics

Your tracing strategy is successful when:

- ✅ **Performance Impact**: <5% overhead in production
- ✅ **Coverage**: Can trace any user-reported issue
- ✅ **Cost**: Trace storage costs <10% of infrastructure budget
- ✅ **Usefulness**: Traces help resolve 80%+ of debugging scenarios
- ✅ **Adoption**: Development team actively uses traces for debugging

***REMOVED******REMOVED*** 🔄 Optimization Cycle

1. **Start Conservative**: 5% sampling in production
2. **Monitor Usage**: How often do you need traces you don't have?
3. **Adjust Strategically**: Increase for critical paths, decrease for bulk operations
4. **Review Costs**: Balance observability value vs. resource cost
5. **Iterate**: Continuously optimize based on real usage patterns

Remember: **Perfect observability isn't worth killing performance.** Find the right balance for your specific use case.
