"""Async utilities for CLI commands.

This module provides async utilities for proper resource cleanup and lifecycle
management, following the patterns discovered in BFF API CLI for enterprise
service orchestration.
"""

from .concurrency import (
    ConcurrentRunner,
    gather_with_timeout,
    run_concurrently,
    run_in_batches,
    run_with_retries,
)
from .context import (
    AsyncResource,
    async_context_manager,
    with_progress,
    with_retry_context,
    with_timeout,
)
from .lifecycle import ManagedService, ServiceLifecycleManager, managed_service

__all__ = [
    "ServiceLifecycleManager",
    "ManagedService",
    "managed_service",
    "async_context_manager",
    "with_progress",
    "with_timeout",
    "with_retry_context",
    "AsyncResource",
    "run_concurrently",
    "gather_with_timeout",
    "run_with_retries",
    "run_in_batches",
    "ConcurrentRunner",
]
