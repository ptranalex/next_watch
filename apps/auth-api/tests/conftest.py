from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel


@pytest.fixture()
def app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Create an isolated Auth API app wired to a temporary SQLite DB."""

    ***REMOVED*** Create a test config first
    from auth_api.config.app import AuthAPIConfig

    db_path = tmp_path / "test.db"
    cfg = AuthAPIConfig(
        environment="test",
        debug=True,
        jwt_secret="test-secret-012345",
        database_url=f"sqlite:///{db_path}",
    )

    ***REMOVED*** Patch global module-level settings used across the app
    import auth_api.config.app as config_app
    import auth_api.db.database as db
    import auth_api.services.auth_service as auth_service_mod

    config_app.settings = cfg
    db.settings = cfg
    auth_service_mod.settings = cfg

    ***REMOVED*** Reset global engine so it rebuilds with the patched settings
    db._engine = None  ***REMOVED*** type: ignore[attr-defined]

    engine = db.get_engine()

    ***REMOVED*** Ensure models are imported/registered, then create tables
    from auth_api.models.user import User  ***REMOVED*** noqa: F401

    SQLModel.metadata.create_all(engine)

    ***REMOVED*** Build the FastAPI app
    from auth_api.core.app_fast_core import create_auth_app

    fastapi_app = create_auth_app(cfg)

    ***REMOVED*** Override DB dependency to ensure tests always hit our SQLite engine
    from auth_api.db.database import get_db

    def override_get_db():
        with Session(engine) as session:
            yield session

    fastapi_app.dependency_overrides[get_db] = override_get_db

    return fastapi_app


@pytest.fixture()
def client(app):
    with TestClient(app) as c:
        yield c
