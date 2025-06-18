"""Async utilities for CLI applications.

Provides helpers for running async operations in CLI commands,
including confirmation dialogs and command runners.
"""

import asyncio
import sys
from typing import Any, Callable, Awaitable, Optional, Dict, List
from rich.console import Console
from rich.prompt import Confirm

from ..output.handler import CLIOutput


async def run_async_command(
    command_func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any
) -> Any:
    """Run an async command function with proper error handling.

    Args:
        command_func: Async function to run
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Result of the command function

    Raises:
        SystemExit: If command fails

    Example:
        >>> async def my_command(name: str):
        ...     return f"Hello {name}"
        >>> result = await run_async_command(my_command, "World")
        >>> print(result)
        Hello World
    """
    try:
        return await command_func(*args, **kwargs)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user", file=sys.stderr)
        raise SystemExit(1)
    except Exception as e:
        print(f"❌ Command failed: {e}", file=sys.stderr)
        raise SystemExit(1)


async def async_input_confirmation(
    message: str, default: bool = False, console: Optional[Console] = None
) -> bool:
    """Async confirmation dialog for CLI operations.

    Args:
        message: Confirmation message to display
        default: Default value if user just presses Enter
        console: Rich console to use

    Returns:
        True if user confirms, False otherwise

    Example:
        >>> confirmed = await async_input_confirmation("Delete all files?")
        >>> if confirmed:
        ...     print("Deleting files...")
    """
    if console is None:
        console = Console()

    ***REMOVED*** Run in thread pool to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, lambda: Confirm.ask(message, default=default, console=console)
    )


class AsyncCommandRunner:
    """Enhanced async command runner with context and error handling."""

    def __init__(
        self,
        output: CLIOutput,
        service_name: str = "cli",
        timeout: Optional[float] = None,
    ):
        """Initialize async command runner.

        Args:
            output: CLI output handler
            service_name: Service name for context
            timeout: Default timeout for operations
        """
        self.output = output
        self.service_name = service_name
        self.timeout = timeout
        self._active_tasks: List[asyncio.Task[Any]] = []

    async def run_with_progress(
        self,
        coro: Awaitable[Any],
        description: str,
        timeout: Optional[float] = None,
    ) -> Any:
        """Run coroutine with progress indicator.

        Args:
            coro: Coroutine to run
            description: Progress description
            timeout: Operation timeout

        Returns:
            Result of the coroutine

        Example:
            >>> runner = AsyncCommandRunner(output)
            >>> result = await runner.run_with_progress(
            ...     slow_operation(), "Processing data..."
            ... )
        """
        effective_timeout = timeout or self.timeout

        try:
            if effective_timeout:
                result = await asyncio.wait_for(coro, timeout=effective_timeout)
            else:
                result = await coro
            return result
        except asyncio.TimeoutError:
            self.output.error(f"Operation timed out after {effective_timeout}s")
            raise
        except Exception as e:
            self.output.error(f"Operation failed: {e}")
            raise

    async def run_concurrent(
        self,
        operations: Dict[str, Awaitable[Any]],
        timeout: Optional[float] = None,
        fail_fast: bool = True,
    ) -> Dict[str, Any]:
        """Run multiple operations concurrently.

        Args:
            operations: Dict of operation name to coroutine
            timeout: Timeout for all operations
            fail_fast: Whether to stop on first failure

        Returns:
            Dict of operation name to result

        Example:
            >>> operations = {
            ...     "check_db": check_database(),
            ...     "check_cache": check_cache(),
            ... }
            >>> results = await runner.run_concurrent(operations)
        """
        effective_timeout = timeout or self.timeout

        if not operations:
            return {}

        self.output.info(f"Running {len(operations)} operations concurrently...")

        ***REMOVED*** Create tasks
        tasks: Dict[str, asyncio.Task[Any]] = {
            name: asyncio.create_task(coro, name=name)  ***REMOVED*** type: ignore[arg-type]
            for name, coro in operations.items()
        }
        self._active_tasks.extend(tasks.values())

        try:
            if fail_fast:
                ***REMOVED*** Wait for all to complete or first to fail
                done, pending = await asyncio.wait(
                    tasks.values(),
                    timeout=effective_timeout,
                    return_when=asyncio.FIRST_EXCEPTION,
                )

                ***REMOVED*** Cancel pending tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                ***REMOVED*** Check for exceptions
                results = {}
                for task in done:
                    if task.exception():
                        raise task.exception()  ***REMOVED*** type: ignore
                    results[task.get_name()] = task.result()

                return results
            else:
                ***REMOVED*** Wait for all to complete, collecting results and errors
                if effective_timeout:
                    done, pending = await asyncio.wait(
                        tasks.values(), timeout=effective_timeout
                    )
                    ***REMOVED*** Cancel pending tasks
                    for task in pending:
                        task.cancel()
                else:
                    ***REMOVED*** Wait for all tasks to complete
                    done = set(tasks.values())

                results = {}
                errors = {}
                for task in done:
                    name = task.get_name()
                    if task.exception():
                        errors[name] = task.exception()
                    else:
                        results[name] = task.result()

                if errors:
                    self.output.warning(
                        f"Some operations failed: {list(errors.keys())}"
                    )
                    for name, error in errors.items():
                        self.output.error(f"{name}: {error}")

                return results

        except asyncio.TimeoutError:
            ***REMOVED*** Cancel all tasks
            for task in tasks.values():
                task.cancel()
            self.output.error(f"Operations timed out after {effective_timeout}s")
            raise
        finally:
            ***REMOVED*** Clean up task references
            for task in tasks.values():
                try:
                    self._active_tasks.remove(task)
                except ValueError:
                    pass

    async def cleanup(self) -> None:
        """Clean up any active tasks."""
        if self._active_tasks:
            self.output.debug(f"Cleaning up {len(self._active_tasks)} active tasks")
            for task in self._active_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            self._active_tasks.clear()

    async def __aenter__(self) -> "AsyncCommandRunner":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.cleanup()
