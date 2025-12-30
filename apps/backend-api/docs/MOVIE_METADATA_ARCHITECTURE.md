# Movie Metadata Architecture: Industry Best Practices

## Overview

This document outlines the optimal architecture for movie metadata aggregation and serving, based on industry leader patterns (Netflix, Amazon Prime, Disney+) and our specific use case where the Backend API serves metadata to the BFF layer for frontend consumption.

## Industry Leader Patterns Analysis

### Netflix Architecture Insights

Based on research, Netflix uses a **multi-layered caching strategy** with these key principles:

1. **Static Data "Cache Forever"** - Movie metadata (cast, genres, descriptions) rarely change
2. **Tiered Storage** - Frequently accessed content in fast storage, long-tail in cheaper storage
3. **CDN Edge Caching** - Metadata cached globally for low latency
4. **Microservices with Circuit Breakers** - Fault-tolerant service composition
5. **Precomputed Aggregations** - Build complete metadata objects ahead of time

### Amazon Prime Video Pattern

- **Multi-tier caching**: Redis → ElastiCache → Database
- **Bulk metadata APIs** with aggressive caching
- **Asynchronous metadata enrichment** pipelines
- **Geographic data distribution** for global scale

## Current Architecture Analysis

### Current Flow

```
Frontend Request → BFF API → Backend API → Database
                          ↓
                   Builds complete movie objects with:
                   - Movie details
                   - Genres (via bulk query)
                   - Cast information
                   - Metadata aggregation
```

### Performance Issues

1. **Real-time aggregation** - Metadata assembled on every request
2. **No caching layer** - Database hit for every metadata request
3. **N+1 query potential** - Despite bulk optimizations
4. **Synchronous processing** - All metadata fetched in request path

## Optimal Architecture for Movie Metadata

### 1. **Precomputed Metadata Store** (Primary Optimization)

**Concept**: Build complete movie metadata objects during content ingestion, not during requests.

```python
# Precomputed movie metadata structure
{
  "movie_id": 123,
  "metadata": {
    "basic_info": {...},
    "genres": [...],
    "cast": [...],
    "crew": {...},
    "ratings": {...},
    "trailers": [...],
    "similar_movies": [...],
    "last_updated": "2024-01-15T10:30:00Z",
    "version": "v2.1"
  }
}
```

**Implementation Strategy**:

```python
# Metadata Builder Service (Background Job)
class MovieMetadataBuilder:
    async def build_complete_metadata(self, movie_id: int):
        """Build complete metadata object for a movie"""
        metadata = {}

        # Fetch all metadata in parallel
        movie_task = self.get_movie_details(movie_id)
        genres_task = self.get_movie_genres(movie_id)
        cast_task = self.get_movie_cast(movie_id)
        crew_task = self.get_movie_crew(movie_id)
        trailers_task = self.get_movie_trailers(movie_id)

        # Wait for all parallel tasks
        results = await asyncio.gather(
            movie_task, genres_task, cast_task,
            crew_task, trailers_task
        )

        # Store in Redis with long TTL
        await self.store_metadata(movie_id, metadata, ttl=30*24*3600)
```

### 2. **Multi-Layer Caching Strategy**

Following Netflix's "cache forever" pattern for static content:

```python
# Layer 1: Redis Cache (Primary)
@redis_cache(ttl=30*24*3600, key_prefix="movie:complete")
async def get_complete_movie_metadata(movie_id: int):
    """Get complete precomputed metadata"""
    pass

# Layer 2: Database Materialized View (Fallback)
CREATE MATERIALIZED VIEW movie_metadata_complete AS
SELECT
    m.*,
    array_agg(DISTINCT jsonb_build_object('id', g.id, 'name', g.name)) as genres,
    array_agg(DISTINCT jsonb_build_object('name', c.name, 'character', c.character))
        FILTER (WHERE c.department = 'Acting') as cast
FROM movie m
LEFT JOIN movie_genre_link mgl ON m.id = mgl.movie_id
LEFT JOIN genre g ON mgl.genre_id = g.id
LEFT JOIN credit c ON m.id = c.movie_id
GROUP BY m.id;

# Layer 3: Hot Cache Warming
class CacheWarmer:
    async def warm_popular_movies(self):
        """Proactively cache popular movie metadata"""
        popular_movies = await self.get_trending_movies(limit=1000)
        await asyncio.gather(*[
            self.get_complete_movie_metadata(movie_id)
            for movie_id in popular_movies
        ])
```

### 3. **Bulk Metadata Endpoint Optimization**

Transform the bulk endpoint to leverage precomputed metadata:

```python
@router.get("/movies/bulk", response_model=MoviesListResponse)
@redis_cache(
    ttl=24*3600,  # 24 hours for bulk responses
    key_builder=lambda ids, page, limit: f"movies:bulk:v2:{hash(tuple(sorted(ids)))}:{page}:{limit}"
)
async def get_movies_bulk_optimized(
    ids: str,
    page: int = 1,
    limit: int = 100,
    cache_manager: CacheManager = Depends(get_cache_manager)
):
    """Optimized bulk endpoint using precomputed metadata"""
    movie_ids = parse_movie_ids(ids)

    # Try to get from cache first (batch operation)
    cached_movies = await cache_manager.mget([
        f"movie:complete:{movie_id}" for movie_id in movie_ids
    ])

    # Identify cache misses
    cache_misses = [
        movie_id for i, movie_id in enumerate(movie_ids)
        if cached_movies[i] is None
    ]

    # Fetch missing movies and warm cache
    if cache_misses:
        await background_warm_cache(cache_misses)
        # Fallback to database for immediate response
        missing_movies = await get_movies_from_db(cache_misses)
        # Fill in the gaps
        for movie in missing_movies:
            cached_movies[movie_ids.index(movie['id'])] = movie

    # Apply pagination and return
    return paginate_movies(cached_movies, page, limit)
```

### 4. **Versioned Metadata with Smart Invalidation**

Implement versioning for cache invalidation without manual cache clearing:

```python
class VersionedMetadata:
    def get_cache_key(self, movie_id: int, version: Optional[str] = None):
        """Generate versioned cache key"""
        if not version:
            # Get latest version from database
            version = await self.get_latest_version(movie_id)
        return f"movie:complete:{movie_id}:v{version}"

    async def update_movie_metadata(self, movie_id: int):
        """Update metadata and increment version"""
        # Increment version
        new_version = await self.increment_version(movie_id)

        # Build new metadata
        metadata = await self.build_complete_metadata(movie_id)

        # Store with new version
        cache_key = self.get_cache_key(movie_id, new_version)
        await self.cache_manager.set(cache_key, metadata, ttl=30*24*3600)

        # Old versions will naturally expire
```

### 5. **Asynchronous Metadata Pipeline**

Background processing for metadata enrichment:

```python
# Metadata Pipeline (Background Jobs)
class MetadataPipeline:
    async def process_new_movie(self, movie_id: int):
        """Process newly added movie"""
        # Stage 1: Basic metadata extraction
        await self.extract_basic_metadata(movie_id)

        # Stage 2: Enrich with external data (TMDB, IMDB)
        await self.enrich_external_metadata(movie_id)

        # Stage 3: Build relationships (similar movies, recommendations)
        await self.build_relationships(movie_id)

        # Stage 4: Precompute and cache complete metadata
        await self.build_and_cache_metadata(movie_id)

        # Stage 5: Warm related caches (genre lists, actor filmographies)
        await self.warm_related_caches(movie_id)

# Triggered by movie updates
@router.post("/movies/{movie_id}/refresh-metadata")
async def refresh_movie_metadata(
    movie_id: int,
    background_tasks: BackgroundTasks
):
    """Trigger metadata refresh"""
    background_tasks.add_task(
        MetadataPipeline().process_movie, movie_id
    )
    return {"status": "refresh_scheduled"}
```

### 6. **Geographic Distribution Strategy**

For global performance (following Netflix CDN pattern):

```python
# Regional cache warming
class RegionalCacheManager:
    def __init__(self, region: str):
        self.region = region
        self.cache_prefix = f"region:{region}"

    async def warm_regional_favorites(self):
        """Warm cache with regionally popular content"""
        popular_movies = await self.get_regional_trending(
            region=self.region, limit=500
        )
        await self.bulk_warm_cache(popular_movies)

    async def get_cache_key(self, movie_id: int):
        """Generate region-aware cache key"""
        return f"{self.cache_prefix}:movie:complete:{movie_id}"
```

## Implementation Plan Updates

### Phase 1A: Precomputed Metadata (NEW - Highest Priority) ⚡⚡

**Target**: 80-90% performance improvement for cached content

1. **Create Materialized View** for complete movie metadata
2. **Background job** to build and cache complete metadata objects
3. **Modify bulk endpoint** to use precomputed data
4. **Implement versioned caching** for smart invalidation

### Phase 1B: Enhanced Caching (Updated Priority)

1. **Multi-get operations** for bulk cache retrieval
2. **Cache warming jobs** for popular content
3. **Regional cache distribution** for global performance

### Phase 2: Pipeline Optimization

1. **Async metadata pipeline** for background processing
2. **Smart cache invalidation** based on content updates
3. **Relationship precomputation** (similar movies, recommendations)

## Expected Performance Improvements

### With Precomputed Metadata

- **Cache Hit Scenarios**: 95-99% response time reduction (sub-10ms)
- **Database Load**: 90-95% reduction in database queries
- **Bulk Operations**: Support for 1000+ movies with constant response time
- **Global Performance**: Sub-100ms worldwide with edge caching

### Real-World Metrics Targets

- **P50 Response Time**: < 50ms (currently ~500ms)
- **P95 Response Time**: < 200ms (currently ~2s)
- **Cache Hit Ratio**: > 95% for popular content
- **Database Load**: < 5% of current load

## Technology Stack Recommendations

### Storage Layer

- **Primary Cache**: Redis Cluster with replication
- **Metadata Store**: PostgreSQL with materialized views
- **Object Storage**: S3 for large metadata objects (cast photos, etc.)

### Processing Layer

- **Background Jobs**: Celery/RQ for metadata pipeline
- **Message Queue**: Redis/RabbitMQ for job scheduling
- **Monitoring**: Custom metrics for cache performance

This architecture follows the industry leader pattern of **"precompute everything, cache forever, invalidate smartly"** which is proven to handle millions of requests per second for metadata-heavy applications like Netflix and Amazon Prime Video.
