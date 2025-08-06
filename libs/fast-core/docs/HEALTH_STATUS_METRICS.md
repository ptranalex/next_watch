***REMOVED*** Health Status Metrics Integration

This document describes the health status metrics integration in fast-core, which provides industry-standard health monitoring metrics that eliminate the need for complex Blackbox Exporter JSON parsing.

***REMOVED******REMOVED*** Overview

The fast-core framework now automatically exposes health status metrics through the `/metrics` endpoint whenever health checks are configured. This follows industry best practices used by Spring Boot, Kubernetes, and other platforms.

***REMOVED******REMOVED*** Architecture

***REMOVED******REMOVED******REMOVED*** Integration Points

1. **MetricsRegistry**: Extended with health-specific metrics
2. **HealthCheckRegistry**: Automatically updates metrics when health checks run
3. **Health Endpoints**: Metrics are updated whenever `/health`, `/health/ready`, or `/health/deep` are called

***REMOVED******REMOVED******REMOVED*** Automatic Operation

- ✅ **Zero Configuration**: Health metrics are automatically created when health checks are registered
- ✅ **Real-time Updates**: Metrics are updated every time health checks execute
- ✅ **Category Support**: Metrics include check categories (critical, important, informational)
- ✅ **Performance Tracking**: Response times and execution counts are tracked

***REMOVED******REMOVED*** Available Metrics

***REMOVED******REMOVED******REMOVED*** 1. Overall Service Health Status

```prometheus
service_health_status{service="service-name"}
```

**Values:**

- `3` = healthy (all critical and important services healthy)
- `2` = degraded (critical services healthy, some important services down)
- `1` = unhealthy (any critical service down)
- `0` = unknown (no health checks or error)

***REMOVED******REMOVED******REMOVED*** 2. Individual Health Check Status

```prometheus
health_check_status{service="service-name",check_name="database",check_category="critical"}
```

**Values:**

- `1` = healthy
- `0` = unhealthy

***REMOVED******REMOVED******REMOVED*** 3. Health Check Response Times

```prometheus
health_check_duration_seconds{service="service-name",check_name="database",check_category="critical"}
```

Histogram tracking health check execution times.

***REMOVED******REMOVED******REMOVED*** 4. Health Check Execution Counts

```prometheus
health_check_executions_total{service="service-name",check_name="database",check_category="critical",status="healthy"}
```

Counter tracking health check executions by status.

***REMOVED******REMOVED*** Usage in Services

***REMOVED******REMOVED******REMOVED*** Automatic Integration

If your service already uses fast-core health checks, metrics are automatically available:

```python
***REMOVED*** Your existing health check setup
from fast_core.monitoring import setup_kubernetes_health_checks

***REMOVED*** This automatically enables health metrics
registry = setup_kubernetes_health_checks(app, settings)
```

***REMOVED******REMOVED******REMOVED*** Manual Integration

For custom health check setups:

```python
from fast_core.monitoring import (
    HealthCheckRegistry,
    HealthCheckDefinition,
    HealthCheckCategory,
    initialize_metrics,
)

***REMOVED*** Initialize metrics (required)
metrics_registry = initialize_metrics("my-service")

***REMOVED*** Create health registry
health_registry = HealthCheckRegistry()

***REMOVED*** Add health checks - metrics are automatically updated
health_registry.add_check(HealthCheckDefinition(
    name="database",
    check_func=check_database,
    category=HealthCheckCategory.CRITICAL,
))
```

***REMOVED******REMOVED*** Grafana Integration

***REMOVED******REMOVED******REMOVED*** Replacing Blackbox Complexity

**Before (Complex Blackbox JSON Parsing):**

```promql
(probe_success{job="nextwatch-health-healthy-only"} * 3) or
(probe_success{job="nextwatch-health-degraded-only"} * 2) or
(probe_success{job="nextwatch-health-endpoints"} * 1)
```

**After (Simple Native Metrics):**

```promql
service_health_status{service="bff-api"}
```

***REMOVED******REMOVED******REMOVED*** Recommended Queries

***REMOVED******REMOVED******REMOVED******REMOVED*** Overall Service Health Dashboard

```promql
***REMOVED*** Service health status
service_health_status

***REMOVED*** Service health over time
service_health_status[5m]

***REMOVED*** Services by health status
count by (service) (service_health_status == 3)  ***REMOVED*** healthy
count by (service) (service_health_status == 2)  ***REMOVED*** degraded
count by (service) (service_health_status == 1)  ***REMOVED*** unhealthy
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Individual Health Check Dashboard

```promql
***REMOVED*** Check status by service
health_check_status

***REMOVED*** Failed checks
health_check_status == 0

***REMOVED*** Check response times
rate(health_check_duration_seconds_sum[5m]) / rate(health_check_duration_seconds_count[5m])

***REMOVED*** Check failure rate
rate(health_check_executions_total{status="unhealthy"}[5m])
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Alert Rules

```promql
***REMOVED*** Service unhealthy
service_health_status < 2

***REMOVED*** Critical check failed
health_check_status{check_category="critical"} == 0

***REMOVED*** Check response time high
rate(health_check_duration_seconds_sum[5m]) / rate(health_check_duration_seconds_count[5m]) > 5
```

***REMOVED******REMOVED******REMOVED*** Value Mappings for Grafana

Configure these value mappings in Grafana panels:

| Value | Text      | Color  |
| ----- | --------- | ------ |
| 3     | Healthy   | Green  |
| 2     | Degraded  | Yellow |
| 1     | Unhealthy | Red    |
| 0     | Unknown   | Gray   |

***REMOVED******REMOVED*** Service Examples

***REMOVED******REMOVED******REMOVED*** BFF API Health Metrics

Available metrics:

```prometheus
service_health_status{service="bff-api"}
health_check_status{service="bff-api",check_name="backend_api",check_category="critical"}
health_check_status{service="bff-api",check_name="redis_cache",check_category="important"}
health_check_status{service="bff-api",check_name="auth_api",check_category="important"}
```

***REMOVED******REMOVED******REMOVED*** Backend API Health Metrics

Available metrics:

```prometheus
service_health_status{service="backend-api"}
health_check_status{service="backend-api",check_name="postgres",check_category="critical"}
health_check_status{service="backend-api",check_name="redis_cache",check_category="important"}
```

***REMOVED******REMOVED*** Migration Guide

***REMOVED******REMOVED******REMOVED*** From Blackbox JSON Parsing

1. **Remove complex Blackbox modules** - No longer need `http_health_healthy_only` or `http_health_degraded_only`
2. **Simplify Prometheus jobs** - Use standard scraping of `/metrics` endpoints
3. **Update Grafana queries** - Replace complex Blackbox queries with simple native metrics
4. **Keep external monitoring** - Continue using Blackbox for external/synthetic monitoring

***REMOVED******REMOVED******REMOVED*** Step-by-Step Migration

1. **Phase 1: Verify metrics are available**

   ```bash
   curl http://localhost:8001/metrics | grep health
   ```

2. **Phase 2: Update Grafana queries**

   - Replace Blackbox queries with native metrics
   - Test new queries in Grafana

3. **Phase 3: Simplify monitoring stack**
   - Remove complex Blackbox configurations
   - Keep simple Blackbox for external monitoring

***REMOVED******REMOVED*** Best Practices

***REMOVED******REMOVED******REMOVED*** 1. Health Check Categories

- **CRITICAL**: Essential for service operation (database, core APIs)
- **IMPORTANT**: Affects functionality but not blocking (cache, optional APIs)
- **INFORMATIONAL**: Monitoring and diagnostics only

***REMOVED******REMOVED******REMOVED*** 2. Monitoring Strategy

- **Native Metrics**: Use for detailed health status and internal monitoring
- **Blackbox Monitoring**: Use for external/synthetic monitoring and user experience validation
- **Dual Layer**: Combine both approaches for comprehensive monitoring

***REMOVED******REMOVED******REMOVED*** 3. Alert Configuration

```yaml
***REMOVED*** Critical service down
- alert: ServiceUnhealthy
  expr: service_health_status < 2
  for: 1m
  labels:
    severity: critical

***REMOVED*** Service degraded
- alert: ServiceDegraded
  expr: service_health_status == 2
  for: 5m
  labels:
    severity: warning

***REMOVED*** Critical check failed
- alert: CriticalCheckFailed
  expr: health_check_status{check_category="critical"} == 0
  for: 30s
  labels:
    severity: critical
```

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Metrics Not Appearing

1. **Check metrics registry initialization**:

   ```python
   from fast_core.monitoring.metrics import get_metrics_registry
   registry = get_metrics_registry()
   print(f"Registry: {registry}")
   ```

2. **Verify health checks are registered**:

   ```bash
   curl http://localhost:8001/health/deep
   ```

3. **Check metrics endpoint**:
   ```bash
   curl http://localhost:8001/metrics | grep -E "(service_health|health_check)"
   ```

***REMOVED******REMOVED******REMOVED*** Common Issues

- **Metrics not updating**: Ensure health checks are actually running
- **Missing categories**: Check that health checks have proper categories assigned
- **Stale metrics**: Health checks may be cached - check TTL settings

***REMOVED******REMOVED*** Integration with Existing Services

All NextWatch services already use fast-core health checks, so health metrics are automatically available at:

- **BFF API**: `http://localhost:8001/metrics`
- **Backend API**: `http://localhost:8002/metrics`
- **Search API**: `http://localhost:8003/metrics`
- **Recommendation API**: `http://localhost:8004/metrics`
- **Auth API**: `http://localhost:8005/metrics`

No code changes required - metrics are automatically exposed when health checks are configured.

***REMOVED******REMOVED*** Conclusion

The health status metrics integration provides:

1. **Industry Standard**: Follows patterns used by Spring Boot, Kubernetes, etc.
2. **Simplified Monitoring**: Eliminates complex Blackbox JSON parsing
3. **Better Observability**: Detailed metrics for individual checks and overall status
4. **Zero Configuration**: Automatically works with existing health checks
5. **Grafana Ready**: Simple queries replace complex Blackbox configurations

This approach significantly simplifies monitoring while providing better observability and following industry best practices.
