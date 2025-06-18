"""Health check result display utilities.

Based on the proven patterns from BFF API CLI, this module provides
consistent formatting for health check results from existing health services.
"""

from typing import Dict, Any, Optional, Protocol, Tuple, List
from rich.table import Table
from rich.console import Console

from ..output.handler import CLIOutput


class HealthCheckResult(Protocol):
    """Protocol for health check results from service health_service implementations.

    This matches the pattern used in BFF, Auth, Backend, and Recommendation APIs.
    """

    is_healthy: bool
    status: str
    response_time_ms: Optional[float]
    details: Optional[Dict[str, Any]]
    error: Optional[str]


def display_health_results(
    results: Dict[str, HealthCheckResult],
    out: CLIOutput,
    service_names: Optional[Dict[str, str]] = None,
) -> None:
    """Display health check results in a formatted table.

    Based on the BFF API CLI display pattern with Rich table formatting.

    Args:
        results: Dictionary mapping service keys to health check results
        out: CLI output handler for consistent display
        service_names: Optional mapping of service keys to display names
    """
    if not results:
        out.warning("No health check results to display")
        return

    ***REMOVED*** Default service name mapping
    default_names = {
        "backend_api": "Backend API",
        "recommendation_api": "Recommendation API",
        "auth_api": "Auth API",
        "redis": "Redis Cache",
        "database": "Database",
    }

    names = service_names or default_names

    ***REMOVED*** Create Rich table with BFF-style formatting
    table = Table(
        title="Service Health Status", show_header=True, header_style="bold blue"
    )
    table.add_column("Service", style="cyan", no_wrap=True)
    table.add_column("Status", style="bold")
    table.add_column("Response Time", style="yellow", no_wrap=True)
    table.add_column("Details", style="dim")

    for service_key, result in results.items():
        service_name = names.get(service_key, service_key)

        ***REMOVED*** Status with color coding (matches BFF patterns)
        if result.is_healthy and result.status == "healthy":
            status = "[green]Healthy[/green]"
        elif result.is_healthy and result.status == "degraded":
            status = "[yellow]Degraded[/yellow]"
        elif result.status == "unavailable":
            status = "[yellow]Unavailable[/yellow]"
        else:
            status = "[red]Unhealthy[/red]"

        ***REMOVED*** Response time formatting
        response_time = (
            f"{result.response_time_ms}ms" if result.response_time_ms else "N/A"
        )

        ***REMOVED*** Details (show error or service status)
        if result.error:
            details = f"[red]{result.error}[/red]"
        elif result.details and result.details.get("service_status"):
            details = result.details["service_status"]
        else:
            details = "-"

        table.add_row(service_name, status, response_time, details)

    ***REMOVED*** Display with proper spacing (BFF pattern)
    out.console.print()
    out.console.print(table)
    out.console.print()


def display_single_health_result(
    service_name: str, result: HealthCheckResult, out: CLIOutput
) -> None:
    """Display a single health check result.

    Based on BFF individual service check patterns.

    Args:
        service_name: Human-readable name of the service
        result: Health check result
        out: CLI output handler
    """
    if result.is_healthy:
        out.success(f"{service_name} is healthy!")
        if result.response_time_ms:
            out.info(f"Response time: {result.response_time_ms}ms")
        if result.details and out.verbose:
            for key, value in result.details.items():
                out.info(f"  • {key}: {value}")
    else:
        out.error(f"{service_name} is unhealthy!")
        if result.error:
            out.error(f"Error: {result.error}")


def get_health_summary(results: Dict[str, HealthCheckResult]) -> Tuple[bool, List[str]]:
    """Get overall health summary from results.

    Args:
        results: Dictionary of health check results

    Returns:
        Tuple of (all_healthy, list_of_unhealthy_services)
    """
    all_healthy = all(result.is_healthy for result in results.values())
    unhealthy_services = [
        name for name, result in results.items() if not result.is_healthy
    ]
    return all_healthy, unhealthy_services
