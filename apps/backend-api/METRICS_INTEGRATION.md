***REMOVED*** Backend API Metrics Integration

This document describes the comprehensive metrics monitoring integration for the Backend API using the fast-core metrics framework.

***REMOVED******REMOVED*** Overview

The Backend API now includes production-ready metrics monitoring that tracks:

- **HTTP Request Metrics**: Latency, throughput, error rates (via fast-core middleware)
- **Database Operations**: Query performance, connection pool status, operation counts
- **Movie Operations**: CRUD operations, search performance, bulk operation efficiency
- **Business Logic**: User collections, data validation, consistency checks
- **Performance**: Pagination efficiency, query optimization impact

***REMOVED******REMOVED*** Architecture

***REMOVED******REMOVED******REMOVED*** Metrics Collection Pattern

The Backend API follows the same excellent metrics pattern established in the BFF API:

```python
***REMOVED*** 1. Service-specific metrics class
class BackendMetrics:
    def __init__(self):
        self.registry = get_metrics_registry()
        self._setup_custom_metrics()

***REMOVED*** 2. Decorator-based instrumentation
@track_movie_operation
async def get_movie_details(movie_id: int):
    ***REMOVED*** Automatic timing and error tracking
    pass

***REMOVED*** 3. Manual metrics recording for complex operations
metrics = get_backend_metrics()
if metrics:
    metrics.record_bulk_operation("bulk_get", batch_size, duration)
```

***REMOVED******REMOVED*** Available Metrics

***REMOVED******REMOVED******REMOVED*** HTTP Metrics (via fast-core middleware)

- `http_request_duration_seconds` - Request latency histograms
- `http_requests_total` - Request count by endpoint/status
- `http_requests_in_progress` - Active request gauge

***REMOVED******REMOVED******REMOVED*** Database Metrics

- `backend_database_operations_total` - Database operation counts by table/operation/status
- `backend_database_query_duration_seconds` - Query performance histograms
- `backend_database_connections_active` - Active connection pool size

***REMOVED******REMOVED******REMOVED*** Movie Operation Metrics

- `backend_movie_operations_total` - Movie operation counts (list, detail, search, bulk)
- `backend_movie_search_duration_seconds` - Search performance by complexity
- `backend_movie_bulk_operation_duration_seconds` - Bulk operation efficiency

***REMOVED******REMOVED******REMOVED*** Actor & Cast Metrics

- `backend_actor_operations_total` - Actor-related operation counts
- `backend_cast_retrieval_duration_seconds` - Cast data retrieval performance

***REMOVED******REMOVED******REMOVED*** User Collection Metrics

- `backend_user_collection_operations_total` - Collection operation counts
- `backend_user_collection_size` - Collection size distributions

***REMOVED******REMOVED******REMOVED*** Data Integrity Metrics

- `backend_data_validation_errors_total` - Validation error tracking
- `backend_data_consistency_checks_total` - Data consistency monitoring

***REMOVED******REMOVED******REMOVED*** Performance Metrics

- `backend_pagination_performance_seconds` - Pagination query efficiency
- `backend_query_optimization_impact_seconds` - Optimization effectiveness

***REMOVED******REMOVED*** Metric Labels

All metrics include consistent labeling for effective filtering and grouping:

- `service="backend-api"` - Service identification
- `operation` - Specific operation type (list, search, bulk, etc.)
- `status` - Operation status (success, error, timeout)
- `table` - Database table name (for DB metrics)
- `search_type` - Search operation type (title, advanced, filter_only)
- `batch_size_range` - Categorized batch sizes (1-10, 11-50, etc.)

***REMOVED******REMOVED*** Integration Points

***REMOVED******REMOVED******REMOVED*** 1. Application Startup

```python
***REMOVED*** apps/backend-api/src/backend_api/core/app_fast_core.py
async def backend_lifespan(app: FastAPI):
    ***REMOVED*** Initialize Backend-specific metrics
    metrics_instance = initialize_backend_metrics()
    if metrics_instance:
        app.state.metrics = metrics_instance
```

***REMOVED******REMOVED******REMOVED*** 2. Middleware Configuration

```python
***REMOVED*** Prometheus metrics middleware
middleware.metrics(
    endpoint_path="/metrics",
    include_endpoint=True,
    exclude_paths=["/health", "/docs", "/openapi.json"],
    enabled=True,
)
```

***REMOVED******REMOVED******REMOVED*** 3. Route Instrumentation

```python
***REMOVED*** Automatic operation tracking
@router.get("/search")
@track_search_operation
async def search_movies(...):
    ***REMOVED*** Manual metrics for business logic
    metrics = get_backend_metrics()
    if metrics:
        metrics.record_movie_search("title", filters_count, duration)
```

***REMOVED******REMOVED*** Usage Examples

***REMOVED******REMOVED******REMOVED*** Tracking Database Operations

```python
from backend_api.core.metrics import get_backend_metrics

async def get_movies_from_db(db, limit, offset):
    metrics = get_backend_metrics()
    start_time = time.time()

    try:
        movies = db.query(Movie).limit(limit).offset(offset).all()
        duration = time.time() - start_time

        if metrics:
            metrics.record_database_operation("select", "movies", "success", duration)

        return movies
    except Exception as e:
        duration = time.time() - start_time
        if metrics:
            metrics.record_database_operation("select", "movies", "error", duration)
        raise
```

***REMOVED******REMOVED******REMOVED*** Tracking Business Operations

```python
@track_bulk_operation
async def bulk_movie_operation(movie_ids: List[int]):
    metrics = get_backend_metrics()

    if metrics:
        metrics.record_movie_operation("bulk", "success")
        metrics.record_bulk_operation("bulk_get", len(movie_ids), operation_duration)

    ***REMOVED*** Business logic here
    return movies
```

***REMOVED******REMOVED*** Monitoring Integration

***REMOVED******REMOVED******REMOVED*** Prometheus Configuration

The Backend API is automatically discovered by Prometheus at `backend-api:8000/metrics`:

```yaml
***REMOVED*** infra/monitoring/prometheus/prometheus.prod.yml
- job_name: "nextwatch-services-backend"
  static_configs:
    - targets: ["backend-api:8000"]
  metrics_path: /metrics
```

***REMOVED******REMOVED******REMOVED*** Grafana Dashboards

Metrics are available for visualization in Grafana:

- **Backend Service Overview**: Request rates, latency, error rates
- **Database Performance**: Query performance, connection usage
- **Business Metrics**: Movie operations, search performance
- **User Activity**: Collection operations, data access patterns

***REMOVED******REMOVED******REMOVED*** Alert Rules

Key alerts are configured in Prometheus:

```yaml
***REMOVED*** High error rate
- alert: BackendHighErrorRate
  expr: rate(http_requests_total{service="backend-api",status_code=~"5.."}[5m]) > 0.1

***REMOVED*** Slow database queries
- alert: BackendSlowQueries
  expr: histogram_quantile(0.95, backend_database_query_duration_seconds) > 1.0

***REMOVED*** High bulk operation latency
- alert: BackendSlowBulkOperations
  expr: histogram_quantile(0.95, backend_movie_bulk_operation_duration_seconds) > 5.0
```

***REMOVED******REMOVED*** Testing Metrics

***REMOVED******REMOVED******REMOVED*** 1. Start the Backend API

```bash
cd apps/backend-api
hatch shell
python -m backend_api
```

***REMOVED******REMOVED******REMOVED*** 2. Generate Test Traffic

```bash
***REMOVED*** Test movie operations
curl http://localhost:8000/api/v1/movies
curl http://localhost:8000/api/v1/movies/1
curl http://localhost:8000/api/v1/movies/search?q=batman

***REMOVED*** Test bulk operations
curl "http://localhost:8000/api/v1/movies/bulk?ids=1,2,3,4,5"
```

***REMOVED******REMOVED******REMOVED*** 3. Check Metrics Endpoint

```bash
curl http://localhost:8000/metrics | grep backend_
```

Expected output:

```prometheus
***REMOVED*** HELP backend_movie_operations_total Total movie-related operations
***REMOVED*** TYPE backend_movie_operations_total counter
backend_movie_operations_total{operation="detail",service="backend-api",status="success"} 1

***REMOVED*** HELP backend_movie_search_duration_seconds Duration of movie search operations
***REMOVED*** TYPE backend_movie_search_duration_seconds histogram
backend_movie_search_duration_seconds_bucket{filters_count="none",search_type="title",service="backend-api",le="0.01"} 1
```

***REMOVED******REMOVED*** Production Deployment

***REMOVED******REMOVED******REMOVED*** Metrics are automatically enabled when:

1. Backend API starts with fast-core integration
2. Prometheus middleware is configured
3. Service discovery includes backend-api:8000
4. Grafana dashboards import backend metrics

***REMOVED******REMOVED******REMOVED*** Performance Impact

- **Memory**: ~2-5MB additional memory for metrics collection
- **CPU**: <1% additional CPU overhead
- **Storage**: ~1KB/minute of metrics data
- **Network**: ~10KB/scrape interval to Prometheus

***REMOVED******REMOVED*** Best Practices

***REMOVED******REMOVED******REMOVED*** 1. Label Cardinality

- Use bounded label values (batch_size_range vs exact batch_size)
- Avoid user-specific labels (user_id, session_id)
- Limit label combinations to prevent metric explosion

***REMOVED******REMOVED******REMOVED*** 2. Histogram Buckets

- Database queries: 1ms to 5s (database-appropriate ranges)
- Business operations: 10ms to 20s (API-appropriate ranges)
- Bulk operations: 100ms to 20s (batch-processing ranges)

***REMOVED******REMOVED******REMOVED*** 3. Error Handling

- Always use try/catch around metrics recording
- Graceful degradation when metrics unavailable
- Never let metrics failures impact business logic

***REMOVED******REMOVED******REMOVED*** 4. Monitoring Focus

- **Golden Signals**: Latency, traffic, errors, saturation
- **Business KPIs**: Search success rate, data integrity, user engagement
- **SLOs**: 99% success rate, <200ms p95 latency, <5s bulk operations

***REMOVED******REMOVED*** Integration with Other Services

The Backend API metrics integrate seamlessly with:

- **BFF API**: Service call metrics show backend performance impact
- **Search API**: Cross-service search performance correlation
- **Auth API**: User authentication impact on backend operations
- **Infrastructure**: Database, Redis, and system metrics correlation

This comprehensive metrics integration provides full observability into the Backend API's performance, reliability, and business impact within the NextWatch platform.
