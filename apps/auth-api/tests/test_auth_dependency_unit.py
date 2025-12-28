"""Unit tests for auth dependencies."""

import pytest
from fastapi import HTTPException


def test_get_current_user_raises_401_when_missing_user() -> None:
    from auth_api.dependencies.auth import get_current_user

    class FakeAuthService:
        def get_user_by_token(self, session, token):
            return None

    with pytest.raises(HTTPException) as exc:
        ***REMOVED*** session isn't used by FakeAuthService
        import asyncio

        asyncio.run(get_current_user(token="t", session=None, auth_service=FakeAuthService()))

    assert exc.value.status_code == 401
