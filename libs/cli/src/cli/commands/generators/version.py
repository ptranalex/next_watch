"""Version command generator for CLI applications.

Provides standardized version commands with consistent formatting,
environment information, and optional verbose details.
"""

import importlib.metadata
import platform
import sys
from collections.abc import Callable
from typing import Any

import typer
from rich.table import Table

from cli.output.handler import get_cli_output


def create_version_command(
    service_name: str,
    package_name: str | None = None,
    default_version: str = "0.1.0",
    config_getter: Callable[[], Any] | None = None,
    show_environment: bool = True,
    show_python_info: bool = True,
    dependencies: list[str] | None = None,
    extra_info: dict[str, str] | None = None,
) -> Callable[..., None]:
    """Create a standardized version command for a service.

    Args:
        service_name: Display name of the service (e.g., "BFF API")
        package_name: Package name for version lookup (defaults to service_name with underscores)
        default_version: Fallback version if package version not found
        config_getter: Optional function to get configuration (for environment info)
        show_environment: Whether to show environment information
        show_python_info: Whether to show Python version
        dependencies: List of key dependencies to show in verbose mode
        extra_info: Additional key-value pairs to display

    Returns:
        Typer command function for version display

    Example:
        >>> version_cmd = create_version_command(
        ...     service_name="BFF API",
        ...     package_name="bff_api",
        ...     config_getter=get_settings,
        ...     dependencies=["fastapi", "redis", "httpx"],
        ...     extra_info={"Database": "PostgreSQL"}
        ... )
        >>> app.command("version")(version_cmd)
    """
    ***REMOVED*** Default package name from service name
    if package_name is None:
        package_name = service_name.lower().replace(" ", "_").replace("-", "_")

    def version_command(
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Show detailed version information"
        ),
        quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output except errors"),
    ) -> None:
        """Show service version information."""
        out = get_cli_output("version", verbose=verbose, quiet=quiet)

        try:
            ***REMOVED*** Get package version
            try:
                version = importlib.metadata.version(package_name)
            except (importlib.metadata.PackageNotFoundError, AttributeError):
                version = default_version

            ***REMOVED*** Basic version info
            out.info(f"[bold blue]{service_name}[/bold blue] version [green]{version}[/green]")

            ***REMOVED*** Environment information
            if show_environment and config_getter:
                try:
                    config = config_getter()
                    if hasattr(config, "environment"):
                        out.info(f"Environment: [yellow]{config.environment}[/yellow]")
                except Exception:
                    ***REMOVED*** Don't fail if config is unavailable
                    pass

            ***REMOVED*** Python version
            if show_python_info:
                out.info(f"Python: [dim]{sys.version.split()[0]}[/dim]")

            ***REMOVED*** Extra info
            if extra_info:
                for key, value in extra_info.items():
                    out.info(f"{key}: [cyan]{value}[/cyan]")

            ***REMOVED*** Verbose mode - detailed information
            if verbose:
                _show_verbose_info(
                    out,
                    service_name,
                    version,
                    package_name,
                    dependencies,
                    config_getter,
                )

                ***REMOVED*** Log operation for monitoring
                out.log_operation(
                    "Version command completed",
                    service=service_name,
                    version=version,
                    package=package_name,
                )

        except Exception as e:
            out.error(f"Error getting version: {e}")
            out.log_error("Version command failed", e, service=service_name)
            raise typer.Exit(code=1)

    return version_command


def _show_verbose_info(
    out: Any,
    service_name: str,
    version: str,
    package_name: str,
    dependencies: list[str] | None,
    config_getter: Callable[[], Any] | None,
) -> None:
    """Show detailed version information in verbose mode."""

    ***REMOVED*** System Information Table
    system_table = Table(title="System Information")
    system_table.add_column("Component", style="cyan")
    system_table.add_column("Version", style="white")

    system_table.add_row("Service", service_name)
    system_table.add_row("Package Version", version)
    system_table.add_row("CLI Framework", "NextWatch CLI Framework v0.3.0")
    system_table.add_row("Python", platform.python_version())
    system_table.add_row("Platform", platform.platform())
    system_table.add_row("System", f"{platform.system()} {platform.release()}")

    ***REMOVED*** Add environment details if available
    if config_getter:
        try:
            config = config_getter()
            if hasattr(config, "environment"):
                system_table.add_row("Environment", config.environment)
            if hasattr(config, "debug") and config.debug:
                system_table.add_row("Debug Mode", "Enabled")
        except Exception:
            pass

    out.console.print(system_table)

    ***REMOVED*** Dependencies Table (if provided)
    if dependencies:
        deps_table = Table(title="Key Dependencies")
        deps_table.add_column("Package", style="cyan")
        deps_table.add_column("Version", style="green")

        for dep in dependencies:
            try:
                dep_version = importlib.metadata.version(dep)
                deps_table.add_row(dep, dep_version)
            except importlib.metadata.PackageNotFoundError:
                ***REMOVED*** Try to import and get version attribute
                try:
                    module = importlib.import_module(dep)
                    if hasattr(module, "__version__"):
                        dep_version = getattr(module, "__version__")
                    elif hasattr(module, "VERSION"):
                        dep_version = str(getattr(module, "VERSION"))
                    else:
                        dep_version = "unknown"
                    deps_table.add_row(dep, dep_version)
                except ImportError:
                    deps_table.add_row(dep, "[red]not installed[/red]")

        out.console.print(deps_table)


def create_simple_version_command(
    service_name: str,
    version: str,
) -> Callable[..., None]:
    """Create a simple version command with minimal information.

    Args:
        service_name: Display name of the service
        version: Version string to display

    Returns:
        Simple version command function

    Example:
        >>> simple_version = create_simple_version_command("Cache Library", "1.0.0")
        >>> app.command("version")(simple_version)
    """

    def simple_version_command() -> None:
        """Show service version."""
        out = get_cli_output("version", verbose=False, quiet=False)
        out.info(f"[bold blue]{service_name}[/bold blue] v{version}")

    return simple_version_command
