"""Async context manager utilities for CLI operations.

Provides reusable async context managers for common CLI patterns like
timeout handling, progress tracking, and resource management.
"""

import asyncio
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any, TypeVar

import structlog

from ..output.handler import CLIOutput

logger = structlog.get_logger(__name__)
T = TypeVar("T")


@asynccontextmanager
async def async_context_manager(
    setup_fn: Callable[[], Any] | None = None,
    cleanup_fn: Callable[[Any], Any] | None = None,
    timeout: float | None = None,
) -> AsyncIterator[Any]:
    """Generic async context manager with setup/cleanup and timeout.

    Args:
        setup_fn: Optional setup function to call on entry
        cleanup_fn: Optional cleanup function to call on exit
        timeout: Optional timeout for the entire context

    Yields:
        Result of setup_fn or None

    Example:
        >>> async with async_context_manager(
        ...     setup_fn=lambda: create_client(),
        ...     cleanup_fn=lambda client: client.close(),
        ...     timeout=30.0
        ... ) as client:
        ...     await client.do_work()
    """
    resource = None
    try:
        ***REMOVED*** Setup phase
        if setup_fn:
            if timeout:
                resource = await asyncio.wait_for(
                    setup_fn() if asyncio.iscoroutinefunction(setup_fn) else setup_fn(),
                    timeout=timeout,
                )
            else:
                resource = await setup_fn() if asyncio.iscoroutinefunction(setup_fn) else setup_fn()

        ***REMOVED*** Context body
        if timeout:
            async with asyncio.timeout(timeout):
                yield resource
        else:
            yield resource

    except TimeoutError:
        logger.error("Context manager timed out", timeout=timeout)
        raise
    except Exception as e:
        logger.error("Context manager error", error=str(e))
        raise
    finally:
        ***REMOVED*** Cleanup phase
        if cleanup_fn and resource is not None:
            try:
                if asyncio.iscoroutinefunction(cleanup_fn):
                    await cleanup_fn(resource)
                else:
                    cleanup_fn(resource)
            except Exception as e:
                logger.error("Cleanup failed", error=str(e))


@asynccontextmanager
async def with_progress(
    out: CLIOutput, message: str, timeout: float | None = None
) -> AsyncIterator[None]:
    """Context manager for operations with progress indication.

    Args:
        out: CLI output handler
        message: Progress message to display
        timeout: Optional timeout for the operation

    Example:
        >>> async with with_progress(out, "Processing data...", timeout=30):
        ...     await process_data()
    """
    progress = out.progress(message)

    try:
        with progress:  ***REMOVED*** Rich Progress uses regular context manager
            if timeout:
                async with asyncio.timeout(timeout):
                    yield
            else:
                yield
    except TimeoutError:
        out.error(f"Operation timed out after {timeout}s")
        raise
    except Exception as e:
        out.error(f"Operation failed: {e}")
        raise


@asynccontextmanager
async def with_timeout(timeout: float, error_message: str | None = None) -> AsyncIterator[None]:
    """Simple timeout context manager.

    Args:
        timeout: Timeout in seconds
        error_message: Custom error message for timeout

    Example:
        >>> async with with_timeout(30, "Data processing timed out"):
        ...     await process_large_dataset()
    """
    try:
        async with asyncio.timeout(timeout):
            yield
    except TimeoutError:
        if error_message:
            logger.error(error_message, timeout=timeout)
        raise


@asynccontextmanager
async def with_retry_context(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> AsyncIterator[Callable[..., Any]]:
    """Context manager that provides a retry decorator.

    Args:
        retries: Number of retry attempts
        delay: Initial delay between retries
        backoff: Backoff multiplier for delay
        exceptions: Tuple of exceptions to retry on

    Yields:
        Retry decorator function

    Example:
        >>> async with with_retry_context(retries=3) as retry:
        ...     @retry
        ...     async def unreliable_operation():
        ...         await might_fail()
        ...     await unreliable_operation()
    """

    def retry_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < retries:
                        logger.warning(
                            "Operation failed, retrying",
                            attempt=attempt + 1,
                            max_retries=retries,
                            delay=current_delay,
                            error=str(e),
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            "Operation failed after all retries",
                            attempts=retries + 1,
                            error=str(e),
                        )
                        raise

            ***REMOVED*** This shouldn't be reached, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    yield retry_decorator


class AsyncResource:
    """Generic async resource wrapper with proper lifecycle management.

    Can wrap any resource that needs async initialization and cleanup.
    """

    def __init__(
        self,
        init_fn: Callable[[], Any],
        cleanup_fn: Callable[[Any], Any] | None = None,
        name: str = "resource",
    ) -> None:
        """Initialize async resource wrapper.

        Args:
            init_fn: Function to initialize the resource
            cleanup_fn: Optional function to cleanup the resource
            name: Name for logging
        """
        self.init_fn = init_fn
        self.cleanup_fn = cleanup_fn
        self.name = name
        self.resource: Any | None = None
        self.logger = logger.bind(resource_name=name)

    async def __aenter__(self) -> Any:
        """Initialize and return the resource."""
        try:
            if asyncio.iscoroutinefunction(self.init_fn):
                self.resource = await self.init_fn()
            else:
                self.resource = self.init_fn()

            self.logger.info("Resource initialized")
            return self.resource

        except Exception as e:
            self.logger.error("Resource initialization failed", error=str(e))
            raise

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Cleanup the resource."""
        if self.resource is not None and self.cleanup_fn:
            try:
                if asyncio.iscoroutinefunction(self.cleanup_fn):
                    await self.cleanup_fn(self.resource)
                else:
                    self.cleanup_fn(self.resource)

                self.logger.info("Resource cleaned up")

            except Exception as e:
                self.logger.error("Resource cleanup failed", error=str(e))
                raise
            finally:
                self.resource = None
