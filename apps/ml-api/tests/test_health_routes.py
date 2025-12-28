"""Unit tests for ML API health routes."""

from __future__ import annotations

import pytest
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_health_and_ping() -> None:
    from ml_api.routes.health import health_check, ping

    h = await health_check()
    assert h["status"] == "ok"

    p = await ping()
    assert p == {"ping": "pong"}


@pytest.mark.asyncio
async def test_model_health_ok(monkeypatch) -> None:
    from ml_api.routes import health as health_module

    monkeypatch.setattr(
        health_module.embedding_service,
        "get_model_info",
        lambda: {"health": "ok", "model_id": "m", "status": "loaded"},
    )

    res = await health_module.model_health_check()
    assert res["status"] == "ok"


@pytest.mark.asyncio
async def test_model_health_unhealthy_raises(monkeypatch) -> None:
    from ml_api.routes import health as health_module

    monkeypatch.setattr(
        health_module.embedding_service,
        "get_model_info",
        lambda: {"health": "error", "model_id": "m", "status": "error"},
    )

    with pytest.raises(HTTPException):
        await health_module.model_health_check()
