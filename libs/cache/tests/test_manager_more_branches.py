"""Unit tests to cover remaining CacheManager branches."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from cache.manager import CacheManager


@pytest.mark.asyncio
async def test_delete_pattern_unsupported_provider_branch() -> None:
    class ProviderNoPattern:
        async def exists(self, key):
            return False

        async def get_json(self, key):
            return None

        async def set_json(self, key, value, ttl=None):
            return True

        async def delete_key(self, key):
            return True

        async def health_check(self):
            return False

    mgr = CacheManager(provider=ProviderNoPattern())
    assert await mgr.delete_pattern("x*") == 0

    ***REMOVED*** health_check false branch
    assert await mgr.health_check() is False


@pytest.mark.asyncio
async def test_safe_methods_error_paths() -> None:
    provider = AsyncMock()
    provider.get_json = AsyncMock(side_effect=RuntimeError("boom"))
    provider.set_json = AsyncMock(side_effect=RuntimeError("boom"))
    provider.delete_key = AsyncMock(side_effect=RuntimeError("boom"))
    provider.exists = AsyncMock(return_value=False)
    provider.health_check = AsyncMock(side_effect=RuntimeError("boom"))


@pytest.mark.asyncio
async def test_context_manager_calls_close() -> None:
    provider = AsyncMock()
    provider.close = AsyncMock(return_value=None)
    provider.exists = AsyncMock(return_value=False)
    provider.get_json = AsyncMock(return_value=None)
    provider.set_json = AsyncMock(return_value=True)
    provider.delete_key = AsyncMock(return_value=True)
    provider.health_check = AsyncMock(return_value=True)

    async with CacheManager(provider=provider) as mgr:
        assert mgr is not None

    assert provider.close.await_count == 1
