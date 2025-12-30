"""Smoke tests for ML API.

These tests intentionally avoid loading the embedding model (which may require
large downloads) and instead validate lightweight endpoints and module wiring.
"""

from http import HTTPStatus

from fastapi import FastAPI
from fastapi.testclient import TestClient


def _make_app() -> FastAPI:
    # Import inside to ensure coverage sees package import
    from ml_api.routes.health import router as health_router

    app = FastAPI()
    app.include_router(health_router)
    return app


def test_health_endpoint() -> None:
    client = TestClient(_make_app())
    res = client.get("/health")
    assert res.status_code == HTTPStatus.OK
    data = res.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_ping_endpoint() -> None:
    client = TestClient(_make_app())
    res = client.get("/ping")
    assert res.status_code == HTTPStatus.OK
    assert res.json() == {"ping": "pong"}


def test_model_health_is_unavailable_without_loading_model() -> None:
    client = TestClient(_make_app())
    res = client.get("/health/model")

    # By default the model is not loaded, so health should not be ok.
    assert res.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    detail = res.json().get("detail", "")
    assert "Model health" in detail
