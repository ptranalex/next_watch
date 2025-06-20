***REMOVED*** Cache Library Migration Guide

***REMOVED******REMOVED*** Overview

This guide explains how to migrate from using service-specific cache wrapper classes to using the enhanced cache library directly.

***REMOVED******REMOVED*** Why Migrate?

1. **Reduced Code Duplication**: Eliminates duplicate error handling and type checking across services
2. **Simplified Architecture**: Direct access to the cache manager with enhanced methods
3. **Consistent API**: Same interface across all services
4. **Better Maintainability**: Changes to error handling or type safety only need to be made in one place

***REMOVED******REMOVED*** Migration Steps

***REMOVED******REMOVED******REMOVED*** 1. Update Cache Service Files

Replace your service-specific cache wrapper class with direct access to a configured CacheManager:

```python
***REMOVED*** Before
class CacheService:
    def __init__(self, settings_obj=None):
        self.settings = settings_obj or CacheSettings()
        self.cache_manager = CacheManager.from_settings(self.settings)

    async def get_json(self, key):
        try:
            result = await self.cache_manager.get_json(key)
            if isinstance(result, dict):
                return cast(Dict[str, Any], result)
            return None
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None

    ***REMOVED*** More wrapper methods...

***REMOVED*** After
def get_cache() -> CacheManager:
    global _cache_manager

    if _cache_manager is None:
        settings = get_cache_settings()
        _cache_manager = CacheManager.from_settings(settings)

    return _cache_manager
```

***REMOVED******REMOVED******REMOVED*** 2. Update Service Code

Update service code to use the enhanced methods directly:

```python
***REMOVED*** Before
cache_service = get_cache_service()
user_data = await cache_service.get_json("user:123")

***REMOVED*** After
cache = get_cache()
user_data = await cache.get_dict("user:123")
```

***REMOVED******REMOVED******REMOVED*** 3. Maintain Backward Compatibility

To maintain backward compatibility, you can provide aliases:

```python
***REMOVED*** For backward compatibility
get_cache_service = get_cache
close_cache_service = close_cache
```

***REMOVED******REMOVED******REMOVED*** 4. Update Health Checks

Replace service-specific health checks with direct cache health checks:

```python
***REMOVED*** Before
async def health_check():
    cache_service = get_cache_service()
    return await cache_service.health_check()

***REMOVED*** After
async def check_cache_health():
    cache = get_cache()
    return await cache.health_check()
```

***REMOVED******REMOVED*** Enhanced Methods Reference

The cache library now provides these enhanced methods:

| Method                           | Description                             |
| -------------------------------- | --------------------------------------- |
| `get_dict(key)`                  | Get a dictionary value with type safety |
| `get_list(key)`                  | Get a list value with type safety       |
| `get_json_safe(key)`             | Get JSON value with error handling      |
| `set_json_safe(key, value, ttl)` | Set JSON value with error handling      |
| `delete_key_safe(key)`           | Delete key with error handling          |

***REMOVED******REMOVED*** Example Usage

```python
***REMOVED*** Get a dictionary with type safety
user = await cache.get_dict(f"user:{user_id}")

***REMOVED*** Get a list with type safety
movies = await cache.get_list("popular:movies")

***REMOVED*** Set with error handling
success = await cache.set_json_safe("stats:daily", stats_data, ttl=3600)

***REMOVED*** Delete with error handling
removed = await cache.delete_key_safe(f"user:{user_id}:session")
```
