# Cache Refinement Strategy: "Forever" Caching with Versioning

## 1. Static Data: Cache "Forever" with Versioning

    • Set TTL to 30 days or longer (effectively infinite for movie content)
    • Use versioned cache keys based on content update timestamps
    • Apply to: movie details, cast, trailers, similar movies, genres

✅ **Benefits:** Data stays hot, automatic updates without manual eviction, reduces backend load

### Versioning Strategy Options:

```python
# Option A: Timestamp-based (recommended)
cache_key = f"static:movie:{movie_id}:v{movie.updated_at.timestamp()}"

# Option B: Content hash-based (more precise for partial updates)
cache_key = f"static:movie:{movie_id}:{content_hash}"

# Option C: Database version field
cache_key = f"static:movie:{movie_id}:v{movie.version}"
```

⸻

## 2. User Data: Keep Short TTL with Context-Aware Timing

    • **Watchlist/Favorites:** 2-5 minutes (frequent changes)
    • **Ratings:** 10-15 minutes (less frequent changes)
    • **Watch progress:** 30 seconds (real-time updates needed)
    • **User preferences:** 1 hour (rarely changed)

⚠️ **Consider:** Push notifications or WebSocket updates for instant sync

⸻

## 3. Cache Warmer: Smart Preloading & Version-Aware Warming

    • **Version checking:** Only fetch if cache miss or version mismatch
    • **Priority tiers:**
    	- **Tier 1** (every 2 hours): New releases (last 30 days), trending top 50
    	- **Tier 2** (daily): Popular movies (top 500), user favorites
    	- **Tier 3** (weekly): Full catalog refresh for discovery

### Version Checking Strategy:

    1. Get latest `movie.updated_at` from database
    2. Check if cache key exists with that version
    3. Skip warming if current version already cached
    4. Remove old versions during warming (cleanup)

⸻

## 4. Eviction Policy & Memory Management

    • Let Redis auto-evict older keys (via `volatile-lru`)
    • **Active cleanup:** Remove old versions when writing new ones
    • **Memory monitoring:** Track cache size per movie type
    • **Fallback:** Prioritize user data over old static versions during memory pressure

⸻

## 5. Hybrid Data Handling

    • **Movies list responses:** Compose static data + user data separately
    • Cache static list results with versioning
    • Overlay user interactions at request time
    • **Example pattern:** `static_movies_v123` + `user_interactions_batch`

⸻

## 6. Key Naming Convention

```
Static Data:    "static:movie:{movie_id}:v{timestamp}"
User Data:      "user:{user_id}:movie:{movie_id}"
Movies List:    "static:movies_list:{filter_hash}:v{timestamp}"
User Batch:     "user:{user_id}:batch:{movie_ids_hash}"
```

⸻

## 7. Monitoring & Metrics

    • Track cache hit rates by data type (static vs user)
    • Monitor version churn rate (how often static data updates)
    • Alert on excessive cache misses or version conflicts
    • **Dashboard metrics:** cache size, eviction rate, warming effectiveness

⸻

## 8. Migration Strategy

    	• **Phase 1:** ✅ **COMPLETED** - Enable versioned static caching (low risk)
    	- ✅ Versioned cache keys implemented
    	- ✅ 30-day TTL for static movie data
    	- ✅ 7-day TTL for movies lists
    	- ✅ 5min TTL for user interactions
    	- ✅ Flexible version detection (timestamp/hash/fallback)
    	• **Phase 2:** ✅ **COMPLETED** - Optimize user data TTLs based on usage patterns
    	- ✅ Context-aware TTLs: 5min watchlist, 3min batch interactions
    	- ✅ Separate static vs user data caching
    • **Phase 3:** ✅ **COMPLETED** - Implement smart warming with version checks
    	- ✅ VersionAwareWarming class with automatic version detection
    	- ✅ Priority tier warming (Tier 1: 2hr, Tier 2: daily, Tier 3: weekly)
    	- ✅ CLI commands: `warm-priority` and `warm-movie-version`
    	- ✅ Skip warming when versions unchanged (core "forever" strategy)
    • **Phase 4:** 🔄 **IN PROGRESS** - Full deployment with monitoring

⸻

## 9. Edge Cases & Considerations

    • **Clock skew:** Handle version conflicts in distributed systems
    • **Graceful degradation:** Fallback when Redis unavailable
    • **Bulk updates:** Prevent cache storms during mass movie updates
    • **Memory pressure:** Smart cleanup prioritization

⸻

## 10. Implementation Notes

    • **Database changes:** Add `updated_at` triggers to movie-related tables
    • **Cache warming coordination:** Use Redis locks to prevent duplicate warming across BFF instances
    • **Version cleanup:** Implement background job or inline cleanup during writes
    • **Monitoring integration:** Export metrics to your existing monitoring stack
