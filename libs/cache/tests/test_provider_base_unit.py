"""Unit tests for CacheProvider base JSON helpers."""

from __future__ import annotations

import pytest
from cache.providers.base import CacheProvider


class P(CacheProvider):
    def __init__(self):
        super().__init__(key_prefix="")
        self._raw = {}

    async def get_raw(self, key):
        return self._raw.get(key)

    async def set_raw(self, key, value, ttl=None):
        self._raw[key] = value
        return True

    async def delete(self, key):
        return self._raw.pop(key, None) is not None

    async def exists(self, key):
        return key in self._raw

    async def health_check(self):
        return True

    async def delete_pattern(self, pattern: str) -> int:
        return 0


@pytest.mark.asyncio
async def test_get_json_invalid_json_returns_none() -> None:
    p = P()
    await p.set_raw("k", "not-json")
    assert await p.get_json("k") is None


@pytest.mark.asyncio
async def test_set_json_non_serializable_returns_false() -> None:
    p = P()

    class X:
        pass

    ok = await p.set_json("k", X())
    assert ok is False


def test_serialize_deserialize_errors() -> None:
    p = P()
    with pytest.raises(ValueError):
        p._deserialize_json("{")
