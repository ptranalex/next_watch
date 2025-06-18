"""Type definitions for the cache library."""

from typing import Any, Dict, List, Optional, Union
from typing_extensions import TypeAlias

***REMOVED*** Cache value types
CacheValue: TypeAlias = Union[str, int, float, bool, Dict[str, Any], list[Any], None]
CacheKey: TypeAlias = str
TTL: TypeAlias = Optional[int]

***REMOVED*** JSON serializable types
JSONSerializable: TypeAlias = Union[
    str, int, float, bool, None, Dict[str, "JSONSerializable"], List["JSONSerializable"]
]

***REMOVED*** Cache operation results
CacheResult: TypeAlias = Optional[JSONSerializable]
CacheSetResult: TypeAlias = bool
