"""Type definitions for the cache library."""

from typing import Any

# Cache value types
type CacheValue = str | int | float | bool | dict[str, Any] | list[Any] | None
type CacheKey = str
type TTL = int | None

# JSON serializable types
type JSONSerializable = (
    str | int | float | bool | None | dict[str, "JSONSerializable"] | list["JSONSerializable"]
)

# Cache operation results
type CacheResult = JSONSerializable | None
type CacheSetResult = bool
