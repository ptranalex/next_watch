# Bulk Movies Endpoint Performance Optimization Plan

## Overview

This document tracks the optimization plan for the `/movies/bulk` endpoint in the Backend API, following industry best practices for high-performance bulk data retrieval.

## Current Performance Analysis

### Endpoint: `GET /movies/bulk`

- **Location**: `backend-api/src/backend_api/routes/v1/movies.py` (lines 169-247)
- **Current Implementation**: Basic bulk retrieval with pagination
- **Main Performance Bottlenecks**:
  1. Inefficient database query parameter binding
  2. No caching layer
  3. Suboptimal batch processing
  4. Missing database indexes for bulk operations

## Optimization Plan

### Phase 1: Core Database Optimizations (High Priority) ⚡

**Target**: 50-70% performance improvement

#### 1.1 Database Query Optimization

- **Current Issue**: Dynamic parameter binding for each ID
  ```python
  # Current (inefficient)
  placeholders = ",".join([":id" + str(i) for i in range(len(movie_ids))])
  params = {f"id{i}": movie_id for i, movie_id in enumerate(movie_ids)}
  ```
- **Solution**: Use PostgreSQL array operations
  ```python
  # Optimized
  movie_query = "SELECT m.* FROM movie m WHERE m.id = ANY(:movie_ids)"
  result = db_session.execute(text(movie_query), {"movie_ids": movie_ids})
  ```
- **Status**: 🔄 In Progress
- **Files to Modify**:
  - `backend-api/src/backend_api/queries/movie_details.py` (lines 206-211)

#### 1.2 Add Database Indexes

- **Indexes Needed**:

  ```sql
  -- For movie bulk queries
  CREATE INDEX CONCURRENTLY idx_movie_id_bulk ON movie(id) WHERE id IS NOT NULL;

  -- For genre bulk fetching
  CREATE INDEX CONCURRENTLY idx_movie_genre_link_bulk ON movie_genre_link(movie_id, genre_id);

  -- For credits bulk fetching
  CREATE INDEX CONCURRENTLY idx_credit_movie_dept_job ON credit(movie_id, department, job)
  WHERE department IN ('Directing', 'Writing');
  ```

- **Status**: 📋 Planned
- **Migration**: Create new migration file

#### 1.3 Redis Caching Layer

- **Implementation**: Following BFF API caching pattern
- **Cache Strategy**:
  - TTL: 24 hours for bulk movie data
  - Key Pattern: `movies:bulk:{sorted_ids_hash}:{page}:{limit}`
  - Cache individual movies + bulk response
- **Status**: 📋 Planned
- **Files to Create/Modify**:
  - Add caching to bulk endpoint
  - Implement cache warming for popular movie sets

### Phase 2: Response & Connection Optimization (Medium Priority) 🚀

**Target**: 20-30% additional improvement

#### 2.1 Connection Pool Optimization

- **Current**: Basic pool settings
- **Optimize**:
  ```python
  pool_size=20,           # Increased from default
  max_overflow=30,        # Better burst handling
  pool_timeout=30,        # Reasonable timeout
  pool_pre_ping=True,     # Health checks
  ```
- **Status**: 📋 Planned

#### 2.2 Response Compression

- **Add**: GZip middleware for bulk responses
- **Implementation**: `GZipMiddleware` with minimum_size=1000
- **Status**: 📋 Planned

#### 2.3 Enhanced Input Validation

- **Optimize**: Bulk validation instead of per-ID validation
- **Add**: Better error handling for malformed ID lists
- **Status**: 📋 Planned

### Phase 3: Advanced Optimizations (Low Priority) 🔧

**Target**: 10-15% additional improvement for scale

#### 3.1 Request Batching

- **Implementation**: Break very large requests into optimal batches
- **Batch Size**: 100 movies per batch (configurable)
- **Status**: 📋 Future

#### 3.2 Async Database Operations

- **Migration**: Convert to async/await database operations
- **Benefits**: Better concurrency under load
- **Status**: 📋 Future

#### 3.3 Response Streaming

- **For**: Very large bulk responses (>500 movies)
- **Format**: NDJSON streaming
- **Status**: 📋 Future

## Performance Monitoring

### Metrics to Track

1. **Response Time**: P50, P95, P99 latencies
2. **Throughput**: Requests per second
3. **Cache Performance**: Hit ratio, miss penalties
4. **Database Performance**: Query execution time, connection pool usage
5. **Batch Size Impact**: Performance vs. batch size correlation

### Current Instrumentation

- ✅ Basic metrics via `@track_bulk_operation` decorator
- ✅ Database monitoring in place
- 📋 Need: Cache metrics, detailed timing breakdowns

## Implementation Progress

### Completed ✅

- [x] Performance analysis and bottleneck identification
- [x] Optimization plan creation

### In Progress 🔄

- [ ] Database query optimization (Phase 1.1)

### Planned 📋

- [ ] Database indexes (Phase 1.2)
- [ ] Redis caching implementation (Phase 1.3)
- [ ] Connection pool optimization (Phase 2.1)
- [ ] Response compression (Phase 2.2)
- [ ] Enhanced monitoring (Phase 2.3)

### Future 🔮

- [ ] Request batching (Phase 3.1)
- [ ] Async database operations (Phase 3.2)
- [ ] Response streaming (Phase 3.3)

## Testing Strategy

### Performance Tests

1. **Baseline Tests**: Current performance metrics
2. **Load Tests**: Various batch sizes (10, 50, 100, 500, 1000 movies)
3. **Stress Tests**: High concurrency scenarios
4. **Cache Tests**: Cache hit/miss scenarios

### Test Scenarios

- Small batches (1-10 movies)
- Medium batches (50-100 movies)
- Large batches (500-1000 movies)
- Concurrent requests
- Cache cold/warm scenarios

## Expected Performance Improvements

### Phase 1 (Core Optimizations)

- **Database Query Time**: 50-70% reduction
- **Cache Hit Scenarios**: 90-95% response time reduction
- **Overall Endpoint**: 40-60% improvement

### Phase 2 (Enhanced Optimizations)

- **Connection Efficiency**: 20-30% improvement
- **Response Size**: 30-50% reduction (compression)
- **Overall Endpoint**: Additional 20-30% improvement

### Phase 3 (Scale Optimizations)

- **Large Batch Handling**: 2-3x improvement for 500+ movies
- **Concurrency**: 50-100% more concurrent requests
- **Memory Usage**: 30-40% reduction

## Risk Assessment

### Low Risk ✅

- Database query optimization
- Response compression
- Enhanced monitoring

### Medium Risk ⚠️

- Redis caching implementation
- Connection pool changes
- Database indexes (needs maintenance window)

### High Risk 🔴

- Async database migration (breaking changes)
- Response streaming (API contract changes)

## Dependencies

### Infrastructure

- Redis instance (for caching)
- Database migration capability
- Monitoring infrastructure

### Code Dependencies

- `cache` library (Redis decorators)
- Database migration tools
- Performance testing framework

## Timeline Estimate

### Phase 1: 1-2 weeks

- Database query optimization: 2-3 days
- Database indexes: 1-2 days
- Redis caching: 3-5 days
- Testing and validation: 2-3 days

### Phase 2: 1 week

- Connection pool optimization: 1 day
- Response compression: 1 day
- Enhanced monitoring: 2-3 days
- Testing: 2-3 days

### Phase 3: 2-3 weeks (future)

- Async migration: 1-2 weeks
- Request batching: 3-5 days
- Response streaming: 5-7 days

---

**Next Steps**: Begin with Phase 1.1 - Database Query Optimization
**Owner**: Development Team
**Last Updated**: $(date)
