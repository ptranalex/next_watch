"""Health command generators.

Generates health check commands that wrap existing health services,
following the proven BFF API CLI patterns.
"""

import asyncio
from collections.abc import Callable
from typing import Any

import typer
from typer import Typer

from ..output.handler import CLIOutput, get_cli_output
from .display import (
    display_health_results,
    display_single_health_result,
    get_health_summary,
)


def create_health_commands(
    health_service_getter: Callable[[], Any],
    service_checks: dict[str, tuple[str, str]],
    service_names: dict[str, str] | None = None,
) -> Typer:
    """Create health check commands that use existing health service.

    Based on BFF API CLI patterns where health commands call existing
    health_service methods rather than duplicating logic.

    Args:
        health_service_getter: Function that returns the health service instance
        service_checks: Dict mapping command names to (method_name, display_name) tuples
        service_names: Optional mapping for service display names

    Returns:
        Typer app with generated health commands

    Example:
        >>> health_app = create_health_commands(
        ...     health_service_getter=lambda: get_health_service(),
        ...     service_checks={
        ...         "backend": ("check_backend_api", "Backend API"),
        ...         "auth": ("check_auth_api", "Auth API"),
        ...         "reco": ("check_recommendation_api", "Recommendation API")
        ...     }
        ... )
        >>> app.add_typer(health_app, name="health")
    """
    health_app = Typer(help="Health check commands for services")

    # Comprehensive health check command
    @health_app.command(name="check")
    def health_check_all(
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
        quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output except errors"),
    ) -> None:
        """Check health of all services."""
        out = get_cli_output("health", verbose=verbose, quiet=quiet)

        if verbose:
            out.info("[blue]🔍 Starting comprehensive health check...[/blue]")
            out.info("")

        asyncio.run(_run_comprehensive_health_check(health_service_getter, out, service_names))

    # Generate individual service commands
    for command_name, (method_name, display_name) in service_checks.items():
        _create_single_service_command(
            health_app, command_name, method_name, display_name, health_service_getter
        )

    return health_app


def _create_single_service_command(
    app: Typer,
    command_name: str,
    method_name: str,
    display_name: str,
    health_service_getter: Callable[[], Any],
) -> None:
    """Create a single service health check command.

    Args:
        app: Typer app to add command to
        command_name: CLI command name (e.g., "backend")
        method_name: Health service method name (e.g., "check_backend_api")
        display_name: Human-readable service name (e.g., "Backend API")
        health_service_getter: Function to get health service instance
    """

    @app.command(name=command_name)
    def check_single_service(
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
        quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output except errors"),
    ) -> None:
        f"""Check health of {display_name} only."""
        out = get_cli_output(f"health.{command_name}", verbose=verbose, quiet=quiet)
        asyncio.run(_check_single_service(health_service_getter, method_name, display_name, out))


async def _run_comprehensive_health_check(
    health_service_getter: Callable[[], Any],
    out: CLIOutput,
    service_names: dict[str, str] | None = None,
) -> None:
    """Run comprehensive health check using existing health service.

    Based on BFF API CLI pattern where the health service handles all complexity.
    """
    health_service = health_service_getter()

    try:
        out.log_operation("Starting comprehensive health check")

        # Health service handles all the complex orchestration
        results = await health_service.check_all()

        # Framework provides consistent display
        display_health_results(results, out, service_names)

        # Simple success/failure logic
        all_healthy, unhealthy_services = get_health_summary(results)

        if all_healthy:
            out.success("All services are healthy!")
            out.log_operation(
                "Health check completed",
                status="all_healthy",
                service_count=len(results),
            )
            exit_code = 0
        else:
            out.error(f"Some services are unhealthy: {', '.join(unhealthy_services)}")
            out.log_operation(
                "Health check completed",
                status="some_unhealthy",
                unhealthy=unhealthy_services,
            )
            exit_code = 1

        raise typer.Exit(code=exit_code)

    except typer.Exit:
        # Re-raise typer.Exit to let it propagate normally
        raise
    except Exception as e:
        out.error(f"Health check failed: {e}")
        out.log_error("Health check failed", e)
        raise typer.Exit(code=1)
    finally:
        # Ensure proper cleanup
        if hasattr(health_service, "close"):
            await health_service.close()


async def _check_single_service(
    health_service_getter: Callable[[], Any],
    method_name: str,
    service_name: str,
    out: CLIOutput,
) -> None:
    """Check health of a single service using existing health service method.

    Based on BFF individual service check patterns.
    """
    health_service = health_service_getter()

    try:
        out.log_operation(f"Checking {service_name}", service_method=method_name)

        # Call the specific health service method
        check_method = getattr(health_service, method_name)
        result = await check_method()

        # Use framework display utilities
        display_single_health_result(service_name, result, out)

        # Log structured result
        out.log_operation(
            f"{service_name} check completed",
            service_method=method_name,
            status="healthy" if result.is_healthy else "unhealthy",
            response_time_ms=result.response_time_ms,
        )

        exit_code = 0 if result.is_healthy else 1
        raise typer.Exit(code=exit_code)

    except typer.Exit:
        # Re-raise typer.Exit to let it propagate normally
        raise
    except AttributeError:
        out.error(f"Health service does not have method '{method_name}'")
        out.log_operation(
            "Invalid health service method",
            service_method=method_name,
            service_name=service_name,
        )
        raise typer.Exit(code=1)
    except Exception as e:
        out.error(f"Failed to check {service_name}: {e}")
        out.log_error(f"{service_name} check failed", e, service_method=method_name)
        raise typer.Exit(code=1)
    finally:
        # Ensure proper cleanup
        if hasattr(health_service, "close"):
            await health_service.close()
