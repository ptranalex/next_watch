"""Configuration display utilities with Rich table formatting.

Provides universal configuration display functions and command generators
following the Auth API patterns for beautiful, secure config presentation.
"""

from collections.abc import Callable
from typing import Any, Protocol

import typer
from rich.console import Console
from rich.table import Table
from typer import Typer

from ..output.handler import CLIOutput, get_cli_output
from .masking import COMMON_SECRET_FIELDS, mask_sensitive_value


class ConfigProtocol(Protocol):
    """Protocol for configuration objects that can be displayed.

    Configuration classes should implement this protocol to work with
    the framework's display utilities.
    """

    pass


def print_config(
    config: Any,
    console: Console | None = None,
    title: str = "Configuration",
    show_secrets: bool = False,
    secret_fields: list[str] | None = None,
    out: CLIOutput | None = None,
) -> None:
    """Display configuration in a formatted Rich table.

    Universal configuration display function that works with any config object.
    Automatically masks sensitive fields for security.

    Args:
        config: Configuration object (with __dict__ or dict-like)
        console: Rich console instance (optional)
        title: Table title
        show_secrets: Whether to show unmasked sensitive values
        secret_fields: Additional secret field names to mask
        out: CLI output handler (alternative to console)

    Example:
        >>> print_config(my_config, title="Auth API Configuration")
        >>> print_config(my_config, show_secrets=True)  # Development only
    """
    # Use provided console, CLIOutput console, or create new one
    if out:
        display_console = out.console
    elif console:
        display_console = console
    else:
        display_console = Console()

    # Get configuration as dictionary
    if hasattr(config, "__dict__"):
        config_dict = config.__dict__
    elif isinstance(config, dict):
        config_dict = config
    else:
        # Try to extract attributes using dir()
        config_dict = {
            attr: getattr(config, attr)
            for attr in dir(config)
            if not attr.startswith("_") and not callable(getattr(config, attr, None))
        }

    # Combine default secret fields with provided ones
    all_secret_fields = COMMON_SECRET_FIELDS + (secret_fields or [])

    # Create Rich table
    table = Table(title=title, show_header=True, header_style="bold blue")
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    # Add configuration rows
    for key, value in sorted(config_dict.items()):
        # Skip private attributes and methods
        if key.startswith("_"):
            continue

        # Mask sensitive values
        masked_value = mask_sensitive_value(
            value,
            field_name=key,
            secret_fields=all_secret_fields,
            show_secrets=show_secrets,
        )

        # Add styling for different value types
        if isinstance(value, bool):
            styled_value = (
                f"[green]{masked_value}[/green]" if value else f"[red]{masked_value}[/red]"
            )
        elif isinstance(value, int | float) and not show_secrets:
            styled_value = f"[yellow]{masked_value}[/yellow]"
        elif "***" in masked_value:
            styled_value = f"[dim]{masked_value}[/dim]"
        else:
            styled_value = masked_value

        table.add_row(key, styled_value)

    # Display the table
    display_console.print()
    display_console.print(table)
    display_console.print()

    # Show warning if secrets are visible
    if show_secrets:
        display_console.print(
            "[yellow]⚠️ Warning: Sensitive values are visible. "
            "Use with caution in production environments.[/yellow]"
        )
        display_console.print()


def create_config_command(
    config_getter: Callable[[], Any],
    secret_fields: list[str] | None = None,
    command_name: str = "config",
) -> Callable[..., None]:
    """Create a configuration display command function.

    Generates a Typer command function that displays configuration
    following the Auth API CLI patterns.

    Args:
        config_getter: Function that returns the configuration object
        secret_fields: Additional secret field names to mask
        command_name: Name for the command (default: "config")

    Returns:
        Typer command function ready to be added to CLI app

    Example:
        >>> config_command = create_config_command(
        ...     lambda: get_config(),
        ...     secret_fields=["custom_secret"]
        ... )
        >>> app.command("config")(config_command)
    """

    def config_command(
        show_secrets: bool = typer.Option(
            False,
            "--show-secrets",
            help="Show sensitive configuration values (use with caution)",
        ),
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Show detailed configuration information"
        ),
        quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output except errors"),
    ) -> None:
        """Display current configuration."""
        out = get_cli_output(command_name, verbose=verbose, quiet=quiet)

        try:
            # Get current configuration
            config = config_getter()

            if verbose:
                out.info("[blue]📋 Loading configuration...[/blue]")
                out.info("")

            # Display configuration table
            print_config(
                config=config,
                title=f"{command_name.title()} Configuration",
                show_secrets=show_secrets,
                secret_fields=secret_fields,
                out=out,
            )

            # Log operation for monitoring
            out.log_operation(
                "Configuration displayed",
                show_secrets=show_secrets,
                field_count=len(config.__dict__ if hasattr(config, "__dict__") else {}),
            )

            if verbose:
                out.success("Configuration loaded successfully!")

        except Exception as e:
            out.error(f"Failed to load configuration: {e}")
            out.log_error("Configuration display failed", e)
            raise typer.Exit(code=1)

    return config_command


def create_config_app(
    config_getter: Callable[[], Any],
    secret_fields: list[str] | None = None,
    app_name: str = "config",
) -> Typer:
    """Create a complete configuration Typer app.

    Creates a Typer sub-application with configuration commands.

    Args:
        config_getter: Function that returns the configuration object
        secret_fields: Additional secret field names to mask
        app_name: Name for the Typer app

    Returns:
        Typer app with configuration commands

    Example:
        >>> config_app = create_config_app(lambda: get_config())
        >>> main_app.add_typer(config_app, name="config")
    """
    config_app = Typer(name=app_name, help=f"Configuration management for {app_name}")

    # Add main config display command
    config_app.command("show")(create_config_command(config_getter, secret_fields, "show"))

    # Add alternative command names for convenience
    config_app.command("display")(create_config_command(config_getter, secret_fields, "display"))

    return config_app


def get_config_summary(config: Any) -> dict[str, Any]:
    """Get a summary of configuration for logging/monitoring.

    Args:
        config: Configuration object

    Returns:
        Dictionary with configuration summary (no sensitive data)
    """
    if hasattr(config, "__dict__"):
        config_dict = config.__dict__
    elif isinstance(config, dict):
        config_dict = config
    else:
        config_dict = {
            attr: getattr(config, attr)
            for attr in dir(config)
            if not attr.startswith("_") and not callable(getattr(config, attr, None))
        }

    # Create summary without sensitive data
    summary = {}
    for key, value in config_dict.items():
        if key.startswith("_"):
            continue

        # Mask sensitive values in summary
        masked_value = mask_sensitive_value(value, field_name=key, show_secrets=False)
        summary[key] = masked_value

    return summary
