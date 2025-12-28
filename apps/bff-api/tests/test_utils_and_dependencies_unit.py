"""Unit tests for BFF utility and dependency helpers."""

from __future__ import annotations

import pytest


def test_extract_user_id_from_token_success(monkeypatch) -> None:
    import jwt

    from bff_api.utils import auth as auth_utils

    monkeypatch.setattr(auth_utils.settings, "jwt_secret", "test-secret", raising=False)

    token = jwt.encode({"sub": "123"}, "test-secret", algorithm="HS256")
    assert auth_utils.extract_user_id_from_token(token) == 123


def test_extract_user_id_from_token_missing_sub_lenient(monkeypatch) -> None:
    import jwt

    from bff_api.utils import auth as auth_utils

    monkeypatch.setattr(auth_utils.settings, "jwt_secret", "test-secret", raising=False)

    token = jwt.encode({"nope": "x"}, "test-secret", algorithm="HS256")
    assert auth_utils.extract_user_id_from_token_lenient(token) is None


def test_extract_user_id_from_token_invalid_raises(monkeypatch) -> None:
    from bff_api.utils import auth as auth_utils

    monkeypatch.setattr(auth_utils.settings, "jwt_secret", "test-secret", raising=False)

    with pytest.raises(Exception):
        auth_utils.extract_user_id_from_token("not-a-jwt")


def test_dependency_get_current_user_id(monkeypatch) -> None:
    from bff_api.dependencies.auth import get_current_user_id

    class Creds:
        def __init__(self, token: str | None):
            self.credentials = token

    ***REMOVED*** Missing creds -> exception
    with pytest.raises(Exception):
        get_current_user_id(credentials=Creds(None))

    ***REMOVED*** Valid creds -> returns int
    monkeypatch.setattr(
        "bff_api.dependencies.auth.extract_user_id_from_token", lambda token, **kw: 7
    )
    assert get_current_user_id(credentials=Creds("t")) == 7


def test_dependency_get_optional_user_id(monkeypatch) -> None:
    from bff_api.dependencies.auth import get_optional_user_id

    class Creds:
        def __init__(self, token: str | None):
            self.credentials = token

    assert get_optional_user_id(credentials=None) is None

    monkeypatch.setattr(
        "bff_api.dependencies.auth.extract_user_id_from_token", lambda token, **kw: 9
    )
    assert get_optional_user_id(credentials=Creds("t")) == 9


def test_response_helpers() -> None:
    from bff_api.utils.responses import (
        create_home_screen_response,
        create_movie_detail_response,
        create_movie_list_response,
        create_search_response,
        create_suggestions_response,
    )

    r1 = create_movie_list_response(movies=[], total=0, page=1, per_page=20, message="ok")
    assert r1["pagination"]["page"] == 1
    assert r1["message"] == "ok"

    r2 = create_movie_detail_response(movie={"id": 1})
    assert r2["data"]["id"] == 1

    r3 = create_search_response(results=[], query="q", total=0, page=1, has_next=False)
    assert r3["data"]["query"] == "q"

    r4 = create_home_screen_response([], [], [], [], [])
    assert "featured_movies" in r4["data"]

    r5 = create_suggestions_response([], query="q")
    assert r5["data"]["count"] == 0


def test_error_handling_helpers(monkeypatch) -> None:
    from fast_core.responses import ResponseBuilder

    from bff_api.utils import error_handling

    ***REMOVED*** Avoid invoking real handler internals
    monkeypatch.setattr(error_handling, "handle_service_error", lambda **kwargs: None)

    import asyncio

    asyncio.run(error_handling.handle_backend_error(Exception("x"), operation="op"))

    rb = ResponseBuilder()
    err = error_handling.create_bff_error_response(
        responses=rb,
        page=1,
        limit=20,
        collection_type="watchlist",
        error_message="oops",
        user_id=1,
    )
    assert "error" in err or "metadata" in err

    ctx = error_handling.BackendErrorContext("op", user_id=1)
    assert ctx.service_name == "backend-api"
