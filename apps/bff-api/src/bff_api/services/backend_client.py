"""Backward-compatible backend client imports.

Historically, callers used:

- `from bff_api.services.backend_client import BackendClient`
- `from bff_api.services.backend_client import BackendClientError`

The implementation was moved to `bff_api.services.clients.*`. This module keeps
those imports working without forcing heavy imports from `bff_api.services.__init__`.
"""

from __future__ import annotations

from bff_api.services.clients.base import (
    BackendClientError,
    BackendClientPermanentError,
    BackendClientTransientError,
)
from bff_api.services.clients.facade import BackendClient

__all__ = [
    "BackendClient",
    "BackendClientError",
    "BackendClientTransientError",
    "BackendClientPermanentError",
]
