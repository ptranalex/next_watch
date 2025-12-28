from __future__ import annotations

import pytest

from auth_api.schemas.auth_schemas import UserCreate


def test_user_create_passwords_must_match():
    with pytest.raises(ValueError, match="Passwords do not match"):
        UserCreate(
            email="x@example.com", username=None, password="aaaaaaaa", password_confirm="bbbbbbbb"
        )
