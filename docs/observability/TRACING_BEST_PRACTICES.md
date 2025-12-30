# Tracing Best Practices Guide

This document outlines when and how to enable distributed tracing across different environments.

## 🎯 Core Principle

**Enable tracing strategically based on environment and needs, not universally.**

## 📊 Environment-Specific Configuration

### 🛠️ Development Environment

**Purpose**: Full visibility for debugging and feature development

```bash
# Example (dev): infra/env/development.example or per-service .env/.env.local
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=1.0          # 100% sampling
TRACING_ENDPOINT=http://localhost:4317
```

**Why 100% sampling in development:**

- Debug every request during development
- Understand full request flow
- Performance impact acceptable with low traffic
- Complete trace coverage for testing

### 🧪 Staging/Testing Environment

**Purpose**: Validate tracing works before production + performance testing

```bash
# .env.staging
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=0.3          # 30% sampling
TRACING_ENDPOINT=http://tempo-staging:4317
```

**Why 30% sampling in staging:**

- Test tracing at realistic volumes
- Validate trace correlation across services
- Performance testing with tracing overhead
- Catch tracing-related issues before production

### 🚀 Production Environment

**Purpose**: Essential observability with minimal performance impact

```bash
# Production env (Docker Compose): .env.prod
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=0.05         # 5% sampling
TRACING_ENDPOINT=http://tempo-prod:4317
```

**Why 5% sampling in production:**

- Capture representative request patterns
- Minimize performance and cost impact
- Still get valuable debugging information
- Can increase temporarily for incident investigation

## 🔧 Configuration Strategies

### Strategy 1: Environment Variables (Recommended)

```bash
# Service automatically picks up configuration
export ENABLE_TRACING=true
export TRACING_SAMPLE_RATE=0.1

# Start service - tracing configured automatically
python -m uvicorn app:create_app --factory
```

### Strategy 2: Service-Specific Configuration

```yaml
# Docker Compose (example)
services:
  backend-api:
    environment:
      ENABLE_TRACING: "true"
      TRACING_SAMPLE_RATE: "0.1"

  user-facing-bff:
    environment:
      ENABLE_TRACING: "true"
      TRACING_SAMPLE_RATE: "0.2" # Higher sampling for user-facing service

  internal-ml-api:
    environment:
      ENABLE_TRACING: "true"
      TRACING_SAMPLE_RATE: "0.02" # Lower sampling for high-volume service
```

### Strategy 3: Dynamic Configuration

```python
# For advanced use cases - adaptive sampling
class AdaptiveSampling:
    def get_sample_rate(self, endpoint: str, load: float) -> float:
        if endpoint.startswith("/health"):
            return 0.01  # Low sampling for health checks
        elif endpoint.startswith("/api/critical"):
            return 0.5   # High sampling for critical endpoints
        elif load > 0.8:
            return 0.02  # Reduce sampling under high load
        else:
            return 0.1   # Default sampling
```

## 🎯 When to Enable/Disable Tracing

### ✅ Always Enable Tracing When:

1. **New Service Development**: Full visibility into request flow
2. **Debugging Production Issues**: Increase sampling temporarily
3. **Performance Analysis**: Understand latency bottlenecks
4. **Service Integration**: Validate cross-service communication
5. **Compliance Requirements**: Some regulations require audit trails

### ⚠️ Consider Disabling When:

1. **Emergency Performance Issues**: Temporary disable to reduce overhead
2. **High-Volume Batch Jobs**: May not need request-level tracing
3. **Cost Constraints**: Very high traffic with limited observability budget
4. **Privacy-Sensitive Services**: Some traces may contain PII

### 🔄 Temporarily Increase Sampling When:

```bash
# Incident investigation
export TRACING_SAMPLE_RATE=1.0  # Temporary 100%

# Performance debugging
export TRACING_SAMPLE_RATE=0.5  # Temporary 50%

# Feature rollout validation
export TRACING_SAMPLE_RATE=0.3  # Temporary 30%
```

## 📈 Sampling Rate Guidelines

### Traffic Volume Based

```yaml
Request Volume Guide:
  < 1K requests/day:    100% sampling (no impact)
  1K - 10K requests/day: 50% sampling
  10K - 100K requests/day: 10% sampling
  100K - 1M requests/day: 5% sampling
  > 1M requests/day:     1-2% sampling
```

### Service Type Based

```yaml
Service Type Recommendations:
  User-facing APIs: 10-20% (need good coverage)
  Internal APIs: 5-10% (moderate coverage)
  Background workers: 1-5% (basic coverage)
  Health checks: 0.1% (minimal coverage)
  ML inference: 2-5% (performance sensitive)
```

## 🔍 Advanced Configuration

### Head-Based Sampling (Current Implementation)

```python
# What we implemented - decides at request start
TRACING_SAMPLE_RATE=0.1  # 10% of all requests traced end-to-end
```

**Pros**: Simple, predictable resource usage
**Cons**: May miss important traces (errors, slow requests)

### Tail-Based Sampling (Future Enhancement)

```python
# Advanced - decides after request completes
sample_if:
  - error_occurred: true
  - duration > 1000ms
  - contains_keyword: "payment"
  - random_sample: 0.05
```

**Pros**: Intelligent sampling, catch all errors
**Cons**: More complex, requires buffering

## 🚨 Emergency Controls

### Quick Disable (Emergency)

```bash
# Fastest way to disable tracing
export ENABLE_TRACING=false

# Or reduce to minimum
export TRACING_SAMPLE_RATE=0.001  # 0.1%
```

### Service Restart Required

After changing tracing configuration, services need restart:

```bash
# Graceful restart with new config
docker compose -f infra/compose/prod.yml --env-file .env.prod restart backend-api

# Or for development
pkill -f uvicorn  # Kill and restart manually
```

## 📊 Monitoring Tracing Health

### Key Metrics to Monitor

```yaml
Tracing Health Metrics:
  - trace_export_errors_total
  - trace_export_duration_seconds
  - traces_received_total
  - traces_dropped_total
  - tempo_ingester_traces_received_total
```

### Alerts to Set Up

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

## 🎯 Team Guidelines

### Developer Workflow

```bash
# Starting development work
./scripts/start-monitoring-with-tempo.sh  # Start observability stack
./scripts/start-backend-with-tracing.sh   # Start service with tracing

# During debugging
export TRACING_SAMPLE_RATE=1.0  # Increase sampling temporarily

# Before committing
./scripts/test-tracing-integration.sh  # Validate tracing works
```

### Operations Workflow

```bash
# Production deployment
docker compose -f infra/compose/prod.yml --env-file .env.prod up -d

# Incident investigation
kubectl set env deployment/backend-api TRACING_SAMPLE_RATE=0.5

# Performance optimization
kubectl set env deployment/ml-api TRACING_SAMPLE_RATE=0.01
```

## 🏆 Success Metrics

Your tracing strategy is successful when:

- ✅ **Performance Impact**: <5% overhead in production
- ✅ **Coverage**: Can trace any user-reported issue
- ✅ **Cost**: Trace storage costs <10% of infrastructure budget
- ✅ **Usefulness**: Traces help resolve 80%+ of debugging scenarios
- ✅ **Adoption**: Development team actively uses traces for debugging

## 🔄 Optimization Cycle

1. **Start Conservative**: 5% sampling in production
2. **Monitor Usage**: How often do you need traces you don't have?
3. **Adjust Strategically**: Increase for critical paths, decrease for bulk operations
4. **Review Costs**: Balance observability value vs. resource cost
5. **Iterate**: Continuously optimize based on real usage patterns

Remember: **Perfect observability isn't worth killing performance.** Find the right balance for your specific use case.
