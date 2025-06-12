"""Health check commands for BFF API services."""

import asyncio
from typer import Typer
from typing import Dict, Any

import typer
from rich.table import Table

from bff_api.cli.logging import get_cli_output, CLIOutput
from bff_api.services.health_service import get_health_service, HealthCheckResult

app: Typer = typer.Typer(
    name="health", help="Health check commands for BFF and dependent services."
)


@app.command(name="check")
def health_check(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output except errors",
    ),
) -> None:
    """Check health of BFF and all dependent services.

    This command checks the health of:
    - Backend API service
    - Recommendation API service
    - Auth API service

    Args:
        verbose: Show detailed output including response times
        quiet: Suppress output except errors
    """
    out = get_cli_output("health", verbose=verbose, quiet=quiet)

    if verbose:
        out.info("[blue]🔍 Starting comprehensive health check...[/blue]")
        out.info("")

    ***REMOVED*** Run async health checks using the health service
    asyncio.run(_run_comprehensive_health_check(out))


@app.command(name="backend")
def check_backend(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output except errors",
    ),
) -> None:
    """Check health of Backend API service only.

    Args:
        verbose: Show detailed output
        quiet: Suppress output except errors
    """
    out = get_cli_output("health.backend", verbose=verbose, quiet=quiet)
    asyncio.run(_check_single_service("backend_api", "Backend API", out))


@app.command(name="auth")
def check_auth(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output except errors",
    ),
) -> None:
    """Check health of Auth API service only.

    Args:
        verbose: Show detailed output
        quiet: Suppress output except errors
    """
    out = get_cli_output("health.auth", verbose=verbose, quiet=quiet)
    asyncio.run(_check_single_service("auth_api", "Auth API", out))


@app.command(name="reco")
def check_reco(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output except errors",
    ),
) -> None:
    """Check health of Recommendation API service only.

    Args:
        verbose: Show detailed output
        quiet: Suppress output except errors
    """
    out = get_cli_output("health.reco", verbose=verbose, quiet=quiet)
    asyncio.run(_check_single_service("recommendation_api", "Recommendation API", out))


async def _run_comprehensive_health_check(out: CLIOutput) -> None:
    """Run comprehensive health checks for all services using the health service.

    Args:
        out: CLI output handler
    """
    health_service = get_health_service()

    try:
        out.log_operation("Starting comprehensive health check")
        results = await health_service.check_all()

        ***REMOVED*** Display results in a nice table
        _display_health_results(results, out)

        ***REMOVED*** Determine overall status
        all_healthy = all(result.is_healthy for result in results.values())

        if all_healthy:
            out.success("All services are healthy!")
            out.log_operation(
                "Health check completed", status="all_healthy", service_count=len(results)
            )
            exit_code = 0
        else:
            unhealthy_services = [name for name, result in results.items() if not result.is_healthy]
            out.error(f"Some services are unhealthy: {', '.join(unhealthy_services)}")
            out.log_operation(
                "Health check completed", status="some_unhealthy", unhealthy=unhealthy_services
            )
            exit_code = 1

        raise typer.Exit(code=exit_code)

    except typer.Exit:
        ***REMOVED*** Re-raise typer.Exit to let it propagate normally
        raise
    except Exception as e:
        out.error(f"Health check failed: {e}")
        out.log_error("Health check failed", e)
        raise typer.Exit(code=1)
    finally:
        await health_service.close()


async def _check_single_service(service_key: str, service_name: str, out: CLIOutput) -> None:
    """Check health of a single service using the health service.

    Args:
        service_key: Key to identify the service in health service results
        service_name: Human-readable service name
        out: CLI output handler
    """
    health_service = get_health_service()

    try:
        out.log_operation(f"Checking {service_name}", service_type=service_key)

        ***REMOVED*** Get the appropriate check method
        if service_key == "backend_api":
            result = await health_service.check_backend_api()
        elif service_key == "recommendation_api":
            result = await health_service.check_recommendation_api()
        elif service_key == "auth_api":
            result = await health_service.check_auth_api()
        else:
            raise ValueError(f"Unknown service key: {service_key}")

        if result.is_healthy:
            out.success(f"{service_name} is healthy!")
            if result.response_time_ms:
                out.info(f"Response time: {result.response_time_ms}ms")
            if result.details and out.verbose:
                for key, value in result.details.items():
                    out.info(f"  • {key}: {value}")

            out.log_operation(
                f"{service_name} check completed",
                service_type=service_key,
                status="healthy",
                response_time_ms=result.response_time_ms,
            )
            raise typer.Exit(code=0)
        else:
            out.error(f"{service_name} is unhealthy!")
            if result.error:
                out.error(f"Error: {result.error}")

            out.log_operation(
                f"{service_name} check completed",
                service_type=service_key,
                status="unhealthy",
                error=result.error,
            )
            raise typer.Exit(code=1)

    except typer.Exit:
        ***REMOVED*** Re-raise typer.Exit to let it propagate normally
        raise
    except Exception as e:
        out.error(f"Failed to check {service_name}: {e}")
        out.log_error(f"{service_name} check failed", e, service_type=service_key)
        raise typer.Exit(code=1)
    finally:
        await health_service.close()


def _display_health_results(results: Dict[str, HealthCheckResult], out: CLIOutput) -> None:
    """Display health check results in a formatted table.

    Args:
        results: Dictionary of health check results
        out: CLI output handler
    """
    table = Table(title="Service Health Status", show_header=True, header_style="bold blue")
    table.add_column("Service", style="cyan", no_wrap=True)
    table.add_column("Status", style="bold")
    table.add_column("Response Time", style="yellow", no_wrap=True)
    table.add_column("Details", style="dim")

    ***REMOVED*** Service name mapping for display
    service_names = {
        "backend_api": "Backend API",
        "recommendation_api": "Recommendation API",
        "auth_api": "Auth API",
    }

    for service_key, result in results.items():
        service_name = service_names.get(service_key, service_key)

        ***REMOVED*** Status with color coding
        if result.is_healthy and result.status == "healthy":
            status = "[green]Healthy[/green]"
        elif result.is_healthy and result.status == "degraded":
            status = "[yellow]Degraded[/yellow]"
        elif result.status == "unavailable":
            status = "[yellow]Unavailable[/yellow]"
        else:
            status = "[red]Unhealthy[/red]"

        ***REMOVED*** Response time
        response_time = f"{result.response_time_ms}ms" if result.response_time_ms else "N/A"

        ***REMOVED*** Details (show error or service status)
        if result.error:
            details = f"[red]{result.error}[/red]"
        elif result.details and result.details.get("service_status"):
            details = result.details["service_status"]
        else:
            details = "-"

        table.add_row(service_name, status, response_time, details)

    out.console.print()
    out.console.print(table)
    out.console.print()
