***REMOVED*** Search API Metrics Integration

This document describes the comprehensive metrics monitoring integration for the Search API using the fast-core metrics framework with Redis-specific enhancements.

***REMOVED******REMOVED*** Overview

The Search API now includes production-ready metrics monitoring that tracks:

- **HTTP Request Metrics**: Latency, throughput, error rates (via fast-core middleware)
- **Redis Operations**: Query performance, connection pool status, key management
- **Search Operations**: Movie search, entity search, suggestion performance
- **Query Analytics**: Search patterns, filter usage, query optimization
- **User Behavior**: Search session patterns, suggestion conversion rates
- **Performance**: Pagination patterns, fuzzy search fallbacks, cache efficiency

***REMOVED******REMOVED*** Architecture

***REMOVED******REMOVED******REMOVED*** Metrics Collection Pattern

The Search API follows the **same excellent microservices monitoring pattern** as BFF and Backend APIs:

1. **🏗️ Infrastructure Layer**: Fast-Core provides base HTTP metrics
2. **🔧 Service Layer**: SearchMetrics class provides Redis and search-specific metrics
3. **📊 Business Layer**: Query analytics, user behavior, and search quality metrics

***REMOVED******REMOVED******REMOVED*** Redis-Focused Metrics

Since Search API is Redis-based, we have extensive Redis monitoring:

```python
***REMOVED*** Redis operation tracking
metrics.record_redis_operation("zrange", "suggestion", "success", 0.045)
metrics.record_redis_operation("keys", "entity", "timeout", 2.1)

***REMOVED*** Connection pool monitoring
metrics.update_redis_connection_pool(25)  ***REMOVED*** Active connections

***REMOVED*** Key management tracking
metrics.update_redis_key_count("suggestion", 150000)
metrics.update_redis_key_count("entity", 45000)
```

***REMOVED******REMOVED*** Key Metrics Categories

***REMOVED******REMOVED******REMOVED*** 1. Redis Performance Metrics

| Metric                                | Type      | Description              | Labels                                       |
| ------------------------------------- | --------- | ------------------------ | -------------------------------------------- |
| `search_redis_operations_total`       | Counter   | Total Redis operations   | `operation`, `key_type`, `status`, `service` |
| `search_redis_query_duration_seconds` | Histogram | Redis query duration     | `operation`, `key_type`, `service`           |
| `search_redis_connections_active`     | Gauge     | Active Redis connections | `service`                                    |
| `search_redis_keys_total`             | Gauge     | Total Redis keys by type | `key_type`, `service`                        |

***REMOVED******REMOVED******REMOVED*** 2. Search Operations Metrics

| Metric                    | Type      | Description                | Labels                                         |
| ------------------------- | --------- | -------------------------- | ---------------------------------------------- |
| `search_requests_total`   | Counter   | Total search requests      | `search_type`, `status`, `service`             |
| `search_duration_seconds` | Histogram | Search operation duration  | `search_type`, `result_count_range`, `service` |
| `search_results_count`    | Histogram | Number of results returned | `search_type`, `service`                       |

***REMOVED******REMOVED******REMOVED*** 3. Suggestion Engine Metrics

| Metric                               | Type      | Description                   | Labels                                             |
| ------------------------------------ | --------- | ----------------------------- | -------------------------------------------------- |
| `search_suggestion_requests_total`   | Counter   | Total suggestion requests     | `suggestion_type`, `status`, `service`             |
| `search_suggestion_duration_seconds` | Histogram | Suggestion operation duration | `suggestion_type`, `query_length_range`, `service` |
| `search_suggestion_cache_hits_total` | Counter   | Cache hit/miss counts         | `cache_type`, `status`, `service`                  |

***REMOVED******REMOVED******REMOVED*** 4. Query Analytics Metrics

| Metric                         | Type    | Description              | Labels                                          |
| ------------------------------ | ------- | ------------------------ | ----------------------------------------------- |
| `search_query_patterns_total`  | Counter | Query pattern analysis   | `pattern_type`, `query_length_range`, `service` |
| `search_popular_queries_total` | Counter | Popular query categories | `query_category`, `service`                     |
| `search_filters_usage_total`   | Counter | Search filter usage      | `filter_type`, `filter_value_range`, `service`  |

***REMOVED******REMOVED******REMOVED*** 5. Performance Optimization Metrics

| Metric                              | Type      | Description                 | Labels                                             |
| ----------------------------------- | --------- | --------------------------- | -------------------------------------------------- |
| `search_fuzzy_fallbacks_total`      | Counter   | Fuzzy search fallback usage | `search_type`, `original_results_range`, `service` |
| `search_pagination_patterns_total`  | Counter   | Pagination usage patterns   | `page_range`, `limit_range`, `service`             |
| `search_entity_performance_seconds` | Histogram | Performance by entity type  | `entity_type`, `complexity`, `service`             |

***REMOVED******REMOVED*** Implementation Details

***REMOVED******REMOVED******REMOVED*** Metrics Initialization

```python
***REMOVED*** In search_lifespan() - apps/search-api/src/search_api/core/app_fast_core.py
from search_api.core.metrics import initialize_search_metrics

metrics_instance = initialize_search_metrics()
if metrics_instance:
    logger.info("Search metrics initialized successfully")
    app.state.metrics = metrics_instance
```

***REMOVED******REMOVED******REMOVED*** Route Instrumentation

```python
***REMOVED*** Search endpoints with metrics decorators
@track_movie_search
async def search_movies(...):
    metrics = get_search_metrics()
    if metrics:
        ***REMOVED*** Record query patterns
        metrics.record_query_pattern("movie_search", len(q))
        metrics.record_pagination_usage(page, limit)

        ***REMOVED*** Record filter usage
        for filter_type, filter_value in filters:
            if filter_value is not None:
                metrics.record_filter_usage(filter_type, filter_value)

@track_suggestion_operation
async def get_search_suggestions(...):
    metrics = get_search_metrics()
    if metrics:
        metrics.record_query_pattern("basic_suggestion", len(query))
        metrics.record_suggestion_request("basic", "success", 0.0, len(query))
```

***REMOVED******REMOVED******REMOVED*** Redis Operation Tracking

```python
***REMOVED*** Example: In SuggestionEngine operations
start_time = time.time()
try:
    result = await redis.zrange(key, start, end)
    duration = time.time() - start_time

    metrics = get_search_metrics()
    if metrics:
        metrics.record_redis_operation("zrange", "suggestion", "success", duration)

except asyncio.TimeoutError:
    duration = time.time() - start_time
    if metrics:
        metrics.record_redis_operation("zrange", "suggestion", "timeout", duration)
```

***REMOVED******REMOVED*** Middleware Integration

The Search API uses the fast-core metrics middleware:

```python
***REMOVED*** Configure metrics middleware for Search API monitoring
middleware.metrics(
    endpoint_path="/metrics",
    include_endpoint=True,
    exclude_paths=["/health", "/metrics", "/docs", "/openapi.json", "/favicon.ico"],
    exclude_methods=["OPTIONS"],
    custom_buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0],
    track_request_size=True,
    track_response_size=True,
    enabled=True,
)
```

***REMOVED******REMOVED*** Testing the Integration

***REMOVED******REMOVED******REMOVED*** 1. Start Search API with Metrics

```bash
cd apps/search-api
***REMOVED*** Ensure metrics are enabled (default)
python -m search_api.main
```

***REMOVED******REMOVED******REMOVED*** 2. Generate Search Traffic

```bash
***REMOVED*** Movie searches
curl "http://localhost:8005/api/v1/search?q=inception&page=1&limit=20"
curl "http://localhost:8005/api/v1/search?q=batman&genre_id=28&imdb_rating=7.0"

***REMOVED*** Suggestions
curl "http://localhost:8005/api/v1/search/suggestions?query=star&limit=10"
curl "http://localhost:8005/api/v1/search/suggestions/text?query=marvel&limit=5"

***REMOVED*** Multi-entity search
curl "http://localhost:8005/api/v1/search/all?query=christopher&page=1&limit=15"
```

***REMOVED******REMOVED******REMOVED*** 3. Check Metrics Endpoint

```bash
curl http://localhost:8005/metrics | grep search_
```

Expected output includes:

```
***REMOVED*** HELP search_requests_total Total search requests by type and status
***REMOVED*** TYPE search_requests_total counter
search_requests_total{search_type="movie",service="search-api",status="success"} 5.0

***REMOVED*** HELP search_duration_seconds Duration of search operations
***REMOVED*** TYPE search_duration_seconds histogram
search_duration_seconds_bucket{le="0.1",result_count_range="1-10",search_type="movie",service="search-api"} 3.0

***REMOVED*** HELP search_redis_operations_total Total Redis operations
***REMOVED*** TYPE search_redis_operations_total counter
search_redis_operations_total{key_type="suggestion",operation="zrange",service="search-api",status="success"} 12.0
```

***REMOVED******REMOVED*** Monitoring Queries

***REMOVED******REMOVED******REMOVED*** Prometheus Queries for Search API

```promql
***REMOVED*** Search request rate by type
rate(search_requests_total[5m])

***REMOVED*** Search latency by percentile
histogram_quantile(0.95, rate(search_duration_seconds_bucket[5m]))

***REMOVED*** Redis operation error rate
rate(search_redis_operations_total{status!="success"}[5m]) / rate(search_redis_operations_total[5m])

***REMOVED*** Most popular search types
topk(10, increase(search_requests_total[1h]))

***REMOVED*** Search success rate
rate(search_requests_total{status="success"}[5m]) / rate(search_requests_total[5m])

***REMOVED*** Redis connection pool utilization
search_redis_connections_active / 100  ***REMOVED*** Assuming max 100 connections

***REMOVED*** Suggestion conversion analysis
rate(search_suggestion_conversions_total{conversion_status="converted"}[5m]) /
rate(search_suggestion_conversions_total[5m])

***REMOVED*** Filter usage patterns
topk(5, increase(search_filters_usage_total[1h]))

***REMOVED*** Search quality metrics
rate(search_quality_metrics_total{quality_range="excellent"}[5m])
```

***REMOVED******REMOVED******REMOVED*** Grafana Dashboard Panels

***REMOVED******REMOVED******REMOVED******REMOVED*** Search Performance Panel

- **Request Rate**: `rate(search_requests_total[5m])`
- **Latency P95**: `histogram_quantile(0.95, rate(search_duration_seconds_bucket[5m]))`
- **Error Rate**: `rate(search_requests_total{status!="success"}[5m])`

***REMOVED******REMOVED******REMOVED******REMOVED*** Redis Performance Panel

- **Operation Rate**: `rate(search_redis_operations_total[5m])`
- **Redis Latency**: `histogram_quantile(0.95, rate(search_redis_query_duration_seconds_bucket[5m]))`
- **Connection Pool**: `search_redis_connections_active`

***REMOVED******REMOVED******REMOVED******REMOVED*** Search Analytics Panel

- **Query Patterns**: `increase(search_query_patterns_total[1h])`
- **Filter Usage**: `increase(search_filters_usage_total[1h])`
- **Entity Popularity**: `increase(search_entity_popularity_total[1h])`

***REMOVED******REMOVED*** Production Configuration

***REMOVED******REMOVED******REMOVED*** Enable Metrics in Production

```python
***REMOVED*** apps/search-api/src/search_api/config/app.py
class SearchAPIConfig:
    enable_metrics: bool = True  ***REMOVED*** Default enabled

    ***REMOVED*** Redis monitoring settings
    redis_max_connections: int = 100
    redis_connection_timeout: int = 5

    ***REMOVED*** Search performance settings
    search_timeout_seconds: int = 10
    max_suggestions: int = 100
```

***REMOVED******REMOVED******REMOVED*** Production Monitoring Strategy

1. **Alert on High Error Rates**: > 5% search errors
2. **Alert on High Latency**: P95 > 500ms for searches
3. **Alert on Redis Issues**: Connection pool > 80% or operation timeouts
4. **Monitor Search Quality**: Track result relevance and user satisfaction
5. **Capacity Planning**: Monitor query volume and Redis key growth

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Common Issues

1. **High Redis Latency**

   - Check Redis connection pool settings
   - Monitor Redis key expiration policies
   - Optimize Redis query patterns

2. **Search Timeout Errors**

   - Review search complexity and filters
   - Check Redis performance and memory usage
   - Optimize suggestion engine algorithms

3. **Missing Metrics**
   - Verify metrics initialization in lifespan
   - Check if prometheus_client is available
   - Ensure middleware is properly configured

***REMOVED******REMOVED******REMOVED*** Debugging Commands

```bash
***REMOVED*** Check metrics instance
curl http://localhost:8005/health | jq '.metrics_enabled'

***REMOVED*** Monitor real-time metrics
watch -n 2 'curl -s http://localhost:8005/metrics | grep search_requests_total'

***REMOVED*** Check Redis connection status
redis-cli -h localhost -p 6379 info clients
```

***REMOVED******REMOVED*** Integration with Production Monitoring

The Search API metrics integrate seamlessly with the production monitoring stack:

- **Prometheus**: Scrapes metrics from `search-api:8005/metrics`
- **Grafana**: Displays search-specific dashboards
- **AlertManager**: Sends alerts for search performance issues
- **Loki**: Aggregates search service logs for correlation

All metrics follow the established NextWatch monitoring patterns and naming conventions for consistency across the platform.

***REMOVED******REMOVED*** Next Steps

1. **Enhanced Analytics**: Add user session tracking and search personalization metrics
2. **Performance Optimization**: Use metrics to identify and optimize slow Redis operations
3. **Business Intelligence**: Track search trends and popular content discovery patterns
4. **Quality Improvement**: Implement search result relevance scoring and user feedback metrics
