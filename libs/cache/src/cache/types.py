"""Type definitions for the cache library."""

from typing import Any

***REMOVED*** Cache value types
type CacheValue = str | int | float | bool | dict[str, Any] | list[Any] | None
type CacheKey = str
type TTL = int | None

***REMOVED*** JSON serializable types
type JSONSerializable = (
    str | int | float | bool | None | dict[str, "JSONSerializable"] | list["JSONSerializable"]
)

***REMOVED*** Cache operation results
type CacheResult = JSONSerializable | None
type CacheSetResult = bool
