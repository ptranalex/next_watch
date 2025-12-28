"""Core package for the BFF service.

Keep this package import side-effect free.

Python loads `bff_api.core.__init__` before any submodules (e.g.
`bff_api.core.metrics`). If we import `app_fast_core` here, we can easily create
circular imports during app startup and test collection.
"""

from __future__ import annotations

from typing import Any

__all__ = ["create_app", "create_bff_app"]


def __getattr__(name: str) -> Any:  ***REMOVED*** pragma: no cover
    if name in {"create_app", "create_bff_app"}:
        from bff_api.core.app_fast_core import create_bff_app

        return create_bff_app
    raise AttributeError(name)
