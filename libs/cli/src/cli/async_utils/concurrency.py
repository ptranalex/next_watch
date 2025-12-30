"""Concurrency utilities for async CLI operations.

Provides utilities for running multiple async operations concurrently,
following the patterns from BFF API CLI for multi-service orchestration.
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

import structlog

logger = structlog.get_logger(__name__)
T = TypeVar("T")


async def run_concurrently(
    tasks: dict[str, Awaitable[T]],
    timeout: float | None = None,
    return_exceptions: bool = True,
) -> dict[str, T | Exception]:
    """Run multiple async tasks concurrently with named results.

    Args:
        tasks: Dictionary mapping task names to awaitable objects
        timeout: Optional timeout for all tasks
        return_exceptions: If True, return exceptions instead of raising

    Returns:
        Dictionary mapping task names to results or exceptions

    Example:
        >>> results = await run_concurrently({
        ...     "backend": check_backend_health(),
        ...     "auth": check_auth_health(),
        ...     "db": check_database_health()
        ... }, timeout=30.0)
        >>> if isinstance(results["backend"], Exception):
        ...     print("Backend check failed!")
    """
    if not tasks:
        return {}

    logger.info("Running concurrent tasks", task_count=len(tasks), timeout=timeout)

    try:
        if timeout:
            # Use wait_for with asyncio.gather for timeout support
            results_list = await asyncio.wait_for(
                asyncio.gather(*tasks.values(), return_exceptions=return_exceptions),
                timeout=timeout,
            )
        else:
            # Use gather without timeout
            results_list = await asyncio.gather(
                *tasks.values(), return_exceptions=return_exceptions
            )

        # Map results back to task names
        results: dict[str, T | Exception] = dict(zip(tasks.keys(), results_list))  # type: ignore

        # Log summary
        successes = sum(1 for r in results.values() if not isinstance(r, Exception))
        failures = len(results) - successes

        logger.info(
            "Concurrent tasks completed",
            total_tasks=len(tasks),
            successes=successes,
            failures=failures,
        )

        return results

    except TimeoutError:
        logger.error("Concurrent tasks timed out", timeout=timeout)
        raise
    except Exception as e:
        logger.error("Concurrent tasks failed", error=str(e))
        raise


async def gather_with_timeout(
    *awaitables: Awaitable[T], timeout: float | None = None, return_exceptions: bool = True
) -> list[T | Exception]:
    """Gather multiple awaitables with timeout support.

    Args:
        *awaitables: Awaitable objects to gather
        timeout: Optional timeout in seconds
        return_exceptions: If True, return exceptions instead of raising

    Returns:
        List of results or exceptions in the same order as input

    Example:
        >>> results = await gather_with_timeout(
        ...     fetch_data(),
        ...     fetch_metadata(),
        ...     timeout=10.0
        ... )
    """
    if not awaitables:
        return []

    logger.debug("Gathering awaitables", count=len(awaitables), timeout=timeout)

    try:
        if timeout:
            result = await asyncio.wait_for(
                asyncio.gather(*awaitables, return_exceptions=return_exceptions),
                timeout=timeout,
            )
            return result  # type: ignore[return-value]
        else:
            result = await asyncio.gather(*awaitables, return_exceptions=return_exceptions)
            return result  # type: ignore[return-value]

    except TimeoutError:
        logger.error("Gather operation timed out", timeout=timeout)
        raise


async def run_with_retries(
    coro: Callable[..., Awaitable[T]],
    *args: Any,
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    **kwargs: Any,
) -> T:
    """Run an async function with retry logic.

    Args:
        coro: Async function to run
        *args: Positional arguments for the function
        retries: Number of retry attempts
        delay: Initial delay between retries
        backoff: Backoff multiplier for delay
        exceptions: Tuple of exceptions to retry on
        **kwargs: Keyword arguments for the function

    Returns:
        Result of the function

    Raises:
        The last exception if all retries fail

    Example:
        >>> result = await run_with_retries(
        ...     unreliable_api_call,
        ...     "arg1", "arg2",
        ...     retries=3,
        ...     delay=1.0,
        ...     backoff=2.0,
        ...     keyword_arg="value"
        ... )
    """
    last_exception = None
    current_delay = delay

    for attempt in range(retries + 1):
        try:
            return await coro(*args, **kwargs)
        except exceptions as e:
            last_exception = e
            if attempt < retries:
                logger.warning(
                    "Function failed, retrying",
                    function=coro.__name__,
                    attempt=attempt + 1,
                    max_retries=retries,
                    delay=current_delay,
                    error=str(e),
                )
                await asyncio.sleep(current_delay)
                current_delay *= backoff
            else:
                logger.error(
                    "Function failed after all retries",
                    function=coro.__name__,
                    attempts=retries + 1,
                    error=str(e),
                )
                raise

    # This shouldn't be reached, but just in case
    if last_exception:
        raise last_exception

    # This really shouldn't be reached
    raise RuntimeError("Unexpected end of retry loop")


async def run_in_batches(
    items: list[T],
    batch_func: Callable[[list[T]], Awaitable[Any]],
    batch_size: int = 10,
    timeout_per_batch: float | None = None,
    max_concurrent_batches: int = 3,
) -> list[Any]:
    """Process items in batches with controlled concurrency.

    Args:
        items: List of items to process
        batch_func: Async function that processes a batch of items
        batch_size: Number of items per batch
        timeout_per_batch: Optional timeout for each batch
        max_concurrent_batches: Maximum number of batches to run concurrently

    Returns:
        List of batch results

    Example:
        >>> async def process_batch(items):
        ...     return [await process_item(item) for item in items]
        >>>
        >>> results = await run_in_batches(
        ...     all_items,
        ...     process_batch,
        ...     batch_size=50,
        ...     max_concurrent_batches=3
        ... )
    """
    if not items:
        return []

    # Split items into batches
    batches = [items[i : i + batch_size] for i in range(0, len(items), batch_size)]

    logger.info(
        "Processing items in batches",
        total_items=len(items),
        batch_count=len(batches),
        batch_size=batch_size,
        max_concurrent_batches=max_concurrent_batches,
    )

    results = []
    semaphore = asyncio.Semaphore(max_concurrent_batches)

    async def process_batch_with_semaphore(batch: list[T]) -> Any:
        async with semaphore:
            try:
                if timeout_per_batch:
                    return await asyncio.wait_for(batch_func(batch), timeout=timeout_per_batch)
                else:
                    return await batch_func(batch)
            except Exception as e:
                logger.error("Batch processing failed", batch_size=len(batch), error=str(e))
                raise

    # Process all batches concurrently (limited by semaphore)
    try:
        results = await asyncio.gather(
            *[process_batch_with_semaphore(batch) for batch in batches], return_exceptions=False
        )

        logger.info(
            "Batch processing completed",
            total_batches=len(batches),
            successful_batches=len(results),
        )

        return results

    except Exception as e:
        logger.error("Batch processing failed", error=str(e))
        raise


class ConcurrentRunner:
    """Helper class for managing concurrent operations with context.

    Provides a convenient interface for running multiple operations
    with shared configuration and state management.
    """

    def __init__(self, timeout: float | None = None, max_concurrent: int | None = None) -> None:
        """Initialize concurrent runner.

        Args:
            timeout: Default timeout for operations
            max_concurrent: Maximum number of concurrent operations
        """
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent) if max_concurrent else None
        self.logger = logger.bind(component="concurrent_runner")

    async def run(
        self,
        operations: dict[str, Callable[[], Awaitable[T]]],
        timeout: float | None = None,
    ) -> dict[str, T | Exception]:
        """Run multiple operations concurrently.

        Args:
            operations: Dictionary mapping names to async callables
            timeout: Override timeout for this run

        Returns:
            Dictionary mapping operation names to results or exceptions
        """
        effective_timeout = timeout or self.timeout

        async def run_operation(
            name: str, op: Callable[[], Awaitable[T]]
        ) -> tuple[str, T | Exception]:
            try:
                if self._semaphore:
                    async with self._semaphore:
                        result = await op()
                else:
                    result = await op()
                return name, result
            except Exception as e:
                self.logger.warning("Operation failed", operation=name, error=str(e))
                return name, e

        # Run all operations
        tasks = [run_operation(name, op) for name, op in operations.items()]

        if effective_timeout:
            completed = await asyncio.wait_for(asyncio.gather(*tasks), timeout=effective_timeout)
        else:
            completed = await asyncio.gather(*tasks)

        # Convert back to dictionary
        return dict(completed)
