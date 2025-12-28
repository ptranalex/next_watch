from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

***REMOVED*** Disable OpenTelemetry in tests to avoid noisy exporter retries to localhost:4317.
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
os.environ.setdefault("OTEL_TRACES_EXPORTER", "none")
os.environ.setdefault("OTEL_METRICS_EXPORTER", "none")
os.environ.setdefault("OTEL_LOGS_EXPORTER", "none")


pytestmark = [
    pytest.mark.filterwarnings("ignore::pydantic.PydanticDeprecatedSince20"),
    pytest.mark.filterwarnings("ignore:`regex` has been deprecated.*:DeprecationWarning"),
    pytest.mark.filterwarnings("ignore:'crypt' is deprecated.*:DeprecationWarning"),
    pytest.mark.filterwarnings(
        "ignore:datetime\\.datetime\\.utcnow\\(\\) is deprecated.*:DeprecationWarning"
    ),
]


def test_register_login_verify_refresh_and_me(client: TestClient) -> None:
    email = "user@example.com"
    password = "strong-pass-123"

    ***REMOVED*** Register
    resp = client.post(
        "/auth/v1/users",
        json={
            "email": email,
            "username": "tester",
            "password": password,
            "password_confirm": password,
        },
    )
    assert resp.status_code == 201, resp.text
    user = resp.json()
    assert user["id"] > 0
    assert user["email"] == email
    assert user["username"] == "tester"

    ***REMOVED*** Login (OAuth2 form)
    resp = client.post(
        "/auth/v1/tokens",
        data={"username": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    tokens = resp.json()
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    ***REMOVED*** Verify token
    resp = client.post(
        "/auth/v1/tokens/verify",
        json={"token": tokens["access_token"]},
    )
    assert resp.status_code == 200, resp.text
    verification = resp.json()
    assert verification["valid"] is True
    assert verification["user_id"] == user["id"]
    assert verification["email"] == email
    assert verification["username"] == "tester"

    ***REMOVED*** Current user profile
    resp = client.get(
        "/auth/v1/users/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 200, resp.text
    me = resp.json()
    assert me["id"] == user["id"]
    assert me["email"] == email
    assert me["username"] == "tester"

    ***REMOVED*** Refresh token
    resp = client.put(
        "/auth/v1/tokens",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert resp.status_code == 200, resp.text
    refreshed = resp.json()
    assert refreshed["token_type"] == "bearer"
    assert refreshed["access_token"]
    assert refreshed["refresh_token"]


def test_duplicate_email_returns_conflict(client: TestClient) -> None:
    payload = {
        "email": "dup@example.com",
        "username": "dupuser",
        "password": "strong-pass-123",
        "password_confirm": "strong-pass-123",
    }

    r1 = client.post("/auth/v1/users", json=payload)
    assert r1.status_code == 201, r1.text

    r2 = client.post("/auth/v1/users", json=payload)
    assert r2.status_code == 409, r2.text
    body = r2.json()
    assert "detail" in body
