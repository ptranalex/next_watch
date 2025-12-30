# Materialized View Refresh Strategy

## TL;DR: It's Automatic! 🎉

The `movie_metadata_complete` materialized view **refreshes itself automatically** via database triggers. No scripts needed!

## How It Works

### Database Triggers (Set up in migration)

```sql
✅ Movie data changes → Auto-refresh (1-2 seconds)
✅ Genre changes → Auto-refresh (1-2 seconds)
✅ Cast/crew changes → Auto-refresh (1-2 seconds)
```

**Your job**: Nothing! Just use the data.
**Performance**: 10-100x faster than N+1 queries
**Freshness**: Always up-to-date within 2 seconds

## BFF Endpoint Updates

### Adding New Static Fields

1. Create migration to add field to materialized view
2. Deploy migration (includes one-time refresh)
3. Update BFF response models
4. Done! Auto-refresh handles future updates

### Adding Dynamic Fields

Use hybrid approach:

```python
# Static data from materialized view (fast)
movie_data = get_movies_precomputed_bulk(movie_ids)

# Dynamic data from cache/separate service
live_metrics = get_live_metrics(movie_ids)

# Merge and return
return merge_data(movie_data, live_metrics)
```

## Manual Operations (Rarely Needed)

### Check if view exists and is populated

```sql
SELECT COUNT(*) FROM movie_metadata_complete;
```

### Force refresh (debugging only)

```sql
SELECT refresh_movie_metadata_complete();
```

### Disable auto-refresh (bulk import performance)

```sql
-- Temporarily disable triggers during bulk operations
DROP TRIGGER movie_metadata_refresh_trigger ON movie;
-- ... do bulk import ...
-- Re-enable trigger
-- ... (see migration for trigger creation SQL)
```

## The Netflix Pattern

**Static content** (movie metadata) = Cache forever with auto-invalidation
**Dynamic content** (user metrics) = Separate cache with appropriate TTL

Your materialized view handles the **static content perfectly** - no refresh management needed! 🚀
