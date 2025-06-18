"""Serve command generator for FastAPI applications.

Provides standardized server management commands with consistent configuration,
logging, and operational patterns across all NextWatch services.
"""

import sys
from typing import Any, Callable, Dict, Optional

import typer
import uvicorn
from rich.panel import Panel
from rich.table import Table

from cli.output.handler import CLIOutput, get_cli_output

***REMOVED*** Constants
PRODUCTION_ENV = "production"
DEFAULT_LOG_LEVEL = "INFO"


***REMOVED*** Reusable parameter definitions
HOST_OPTION = typer.Option(
    None,
    "--host",
    "-h",
    help="Host to bind server to",
    envvar="HOST",
)
PORT_OPTION = typer.Option(
    None,
    "--port",
    "-p",
    help="Port to bind server to",
    envvar="PORT",
)
RELOAD_OPTION = typer.Option(
    False,
    "--reload",
    help="Enable auto-reload for development",
)
WORKERS_OPTION = typer.Option(
    None,
    "--workers",
    "-w",
    help="Number of worker processes (ignored in reload mode)",
)
LOG_LEVEL_OPTION = typer.Option(
    None,
    "--log-level",
    help="Set log level (DEBUG, INFO, WARNING, ERROR)",
    envvar="LOG_LEVEL",
)
VERBOSE_OPTION = typer.Option(
    False,
    "--verbose",
    "-v",
    help="Enable verbose logging and output",
)
QUIET_OPTION = typer.Option(
    False,
    "--quiet",
    "-q",
    help="Suppress console output except errors",
)


def create_serve_command(
    service_name: str,
    app_import_string: str,
    get_app_instance: Optional[Callable[[], Any]] = None,
    config_getter: Optional[Callable[[], Any]] = None,
    default_host: str = "0.0.0.0",
    default_port: int = 8000,
    print_config_func: Optional[Callable[[Any, str, Any], None]] = None,
    extra_uvicorn_kwargs: Optional[Dict[str, Any]] = None,
) -> Callable[..., None]:
    """Create a standardized serve command for FastAPI applications.

    Args:
        service_name: Display name of the service (e.g., "BFF API")
        app_import_string: Import string for uvicorn (e.g., "bff_api.main:app")
        get_app_instance: Optional function to get app instance for production mode
        config_getter: Optional function to get configuration
        default_host: Default host to bind to
        default_port: Default port to bind to
        print_config_func: Optional function to print detailed config
        extra_uvicorn_kwargs: Additional kwargs to pass to uvicorn.run

    Returns:
        Typer command function for serving the application

    Example:
        >>> serve_cmd = create_serve_command(
        ...     service_name="BFF API",
        ...     app_import_string="bff_api.main:app",
        ...     get_app_instance=get_app,
        ...     config_getter=get_settings,
        ...     print_config_func=print_config,
        ... )
        >>> app.command("serve")(serve_cmd)
    """

    def serve_command(
        host: Optional[str] = HOST_OPTION,
        port: Optional[int] = PORT_OPTION,
        reload: bool = RELOAD_OPTION,
        workers: Optional[int] = WORKERS_OPTION,
        log_level: Optional[str] = LOG_LEVEL_OPTION,
        verbose: bool = VERBOSE_OPTION,
        quiet: bool = QUIET_OPTION,
    ) -> None:
        """Start the service server."""
        out = get_cli_output("serve", verbose=verbose, quiet=quiet)

        try:
            ***REMOVED*** Get configuration and apply CLI overrides
            config = _get_effective_config(
                config_getter, host, port, log_level, default_host, default_port
            )

            ***REMOVED*** Extract final values
            final_host = config.get("host", default_host)
            final_port = config.get("port", default_port)
            final_log_level = config.get("log_level", DEFAULT_LOG_LEVEL)

            ***REMOVED*** Display startup information
            if not quiet:
                _display_startup_info(
                    out,
                    service_name,
                    final_host,
                    final_port,
                    config,
                    verbose,
                    print_config_func,
                )

            ***REMOVED*** Log operational info
            out.log_operation(
                f"Starting {service_name} server",
                host=final_host,
                port=final_port,
                reload=reload,
                workers=workers,
                log_level=final_log_level,
            )

            ***REMOVED*** Prepare uvicorn arguments
            uvicorn_kwargs = {
                "host": final_host,
                "port": final_port,
                "reload": reload,
                "log_level": final_log_level.lower(),
            }

            ***REMOVED*** Add workers only if not in reload mode
            if workers and isinstance(workers, int) and not reload:
                uvicorn_kwargs["workers"] = workers

            ***REMOVED*** Add access log based on environment
            if config_getter:
                try:
                    cfg = config_getter()
                    if hasattr(cfg, "is_production"):
                        uvicorn_kwargs["access_log"] = not cfg.is_production
                    elif hasattr(cfg, "environment") and isinstance(
                        cfg.environment, str
                    ):
                        uvicorn_kwargs["access_log"] = cfg.environment != PRODUCTION_ENV
                except Exception:
                    pass

            ***REMOVED*** Merge extra kwargs
            if extra_uvicorn_kwargs:
                uvicorn_kwargs.update(extra_uvicorn_kwargs)

            ***REMOVED*** Start server
            if reload or not get_app_instance:
                ***REMOVED*** Use import string for reload mode or when no app instance getter
                uvicorn.run(app_import_string, **uvicorn_kwargs)
            else:
                ***REMOVED*** Use app instance for production mode (more efficient)
                app_instance = get_app_instance()
                uvicorn.run(app_instance, **uvicorn_kwargs)

        except KeyboardInterrupt:
            out.info("Server shutdown requested")
            sys.exit(0)
        except Exception as e:
            out.error(f"Error starting {service_name} server: {e}")
            out.log_error("Server start failed", e, service=service_name)
            raise typer.Exit(code=1)

    return serve_command


def create_serve_app(
    service_name: str,
    app_import_string: str,
    get_app_instance: Optional[Callable[[], Any]] = None,
    config_getter: Optional[Callable[[], Any]] = None,
    default_host: str = "0.0.0.0",
    default_port: int = 8000,
    print_config_func: Optional[Callable[[Any, str, Any], None]] = None,
    extra_uvicorn_kwargs: Optional[Dict[str, Any]] = None,
    include_management_commands: bool = False,
) -> typer.Typer:
    """Create a complete serve command app with optional management commands.

    Args:
        service_name: Display name of the service
        app_import_string: Import string for uvicorn
        get_app_instance: Optional function to get app instance
        config_getter: Optional function to get configuration
        default_host: Default host to bind to
        default_port: Default port to bind to
        print_config_func: Optional function to print detailed config
        extra_uvicorn_kwargs: Additional kwargs to pass to uvicorn.run
        include_management_commands: Whether to include stop/restart commands

    Returns:
        Typer app with serve commands

    Example:
        >>> serve_app = create_serve_app(
        ...     service_name="BFF API",
        ...     app_import_string="bff_api.main:app",
        ...     config_getter=get_settings,
        ...     include_management_commands=True,
        ... )
        >>> main_app.add_typer(serve_app, name="serve")
    """
    app = typer.Typer(
        name="serve",
        help=f"Server management commands for {service_name}",
    )

    ***REMOVED*** Create the main serve command
    serve_cmd = create_serve_command(
        service_name=service_name,
        app_import_string=app_import_string,
        get_app_instance=get_app_instance,
        config_getter=config_getter,
        default_host=default_host,
        default_port=default_port,
        print_config_func=print_config_func,
        extra_uvicorn_kwargs=extra_uvicorn_kwargs,
    )

    ***REMOVED*** Add start command
    app.command("start")(serve_cmd)

    ***REMOVED*** Make serve callback invoke start by default
    @app.callback(invoke_without_command=True)
    def serve_callback(
        ctx: typer.Context,
        host: Optional[str] = HOST_OPTION,
        port: Optional[int] = PORT_OPTION,
        reload: bool = RELOAD_OPTION,
        workers: Optional[int] = WORKERS_OPTION,
        log_level: Optional[str] = LOG_LEVEL_OPTION,
        verbose: bool = VERBOSE_OPTION,
        quiet: bool = QUIET_OPTION,
    ) -> None:
        """Start the server (default action)."""
        if ctx.invoked_subcommand is None:
            ctx.invoke(
                serve_cmd,
                host=host,
                port=port,
                reload=reload,
                workers=workers,
                log_level=log_level,
                verbose=verbose,
                quiet=quiet,
            )

    ***REMOVED*** Add management commands if requested
    if include_management_commands:
        _add_management_commands(app, service_name)

    return app


def _get_effective_config(
    config_getter: Optional[Callable[[], Any]],
    host: Optional[str],
    port: Optional[int],
    log_level: Optional[str],
    default_host: str,
    default_port: int,
) -> Dict[str, Any]:
    """Get effective configuration with CLI overrides."""
    config = {}

    ***REMOVED*** Get base config if available
    if config_getter:
        try:
            cfg = config_getter()
            if hasattr(cfg, "host"):
                config["host"] = cfg.host
            if hasattr(cfg, "port"):
                config["port"] = cfg.port
            if hasattr(cfg, "log_level"):
                config["log_level"] = cfg.log_level
            ***REMOVED*** Store the full config object for other uses
            config["_config_obj"] = cfg
        except Exception:
            pass

    ***REMOVED*** Apply CLI overrides
    if host and isinstance(host, str):
        config["host"] = host
    if port and isinstance(port, int):
        config["port"] = port
    if log_level and isinstance(log_level, str):
        config["log_level"] = log_level.upper()

    ***REMOVED*** Apply defaults
    config.setdefault("host", default_host)
    config.setdefault("port", default_port)
    config.setdefault("log_level", DEFAULT_LOG_LEVEL)

    return config


def _display_startup_info(
    out: CLIOutput,
    service_name: str,
    host: str,
    port: int,
    config: Dict[str, Any],
    verbose: bool,
    print_config_func: Optional[Callable[[Any, str, Any], None]],
) -> None:
    """Display server startup information."""
    ***REMOVED*** Main startup message
    out.console.print(
        Panel.fit(
            f"Starting {service_name} server on {host}:{port}",
            title="Server Start",
            border_style="green",
        )
    )

    ***REMOVED*** Show environment info if available
    config_obj = config.get("_config_obj")
    if config_obj:
        env_info = []
        if hasattr(config_obj, "environment"):
            env_info.append(f"Environment: {config_obj.environment}")
        if hasattr(config_obj, "debug"):
            env_info.append(f"Debug: {config_obj.debug}")

        if env_info:
            out.info(f"[dim]{' | '.join(env_info)}[/dim]")

    ***REMOVED*** Verbose configuration display
    if verbose and config_obj and print_config_func:
        try:
            print_config_func(
                config_obj, f"{service_name} Server Configuration", out.console
            )
        except Exception:
            ***REMOVED*** Fallback to simple table
            _display_simple_config_table(out, config)
    elif verbose:
        _display_simple_config_table(out, config)


def _display_simple_config_table(out: CLIOutput, config: Dict[str, Any]) -> None:
    """Display a simple configuration table."""
    table = Table(title="Server Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Host", config.get("host", "unknown"))
    table.add_row("Port", str(config.get("port", "unknown")))
    table.add_row("Log Level", config.get("log_level", "unknown"))

    out.console.print(table)


def _add_management_commands(app: typer.Typer, service_name: str) -> None:
    """Add stop and restart management commands."""

    @app.command()
    def stop(
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Show detailed stop information"
        ),
    ) -> None:
        """Stop the server (placeholder - requires process management)."""
        out = get_cli_output("stop", verbose=verbose)

        out.warning(f"Stopping {service_name} server...")
        out.info("Note: This is a placeholder command.")
        out.info("To stop the server, press Ctrl+C in the terminal where it's running.")
        out.info(
            "For production deployments, use your process manager (systemd, supervisor, etc.)"
        )

    @app.command()
    def restart(
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Show detailed restart information"
        ),
    ) -> None:
        """Restart the server (placeholder - requires process management)."""
        out = get_cli_output("restart", verbose=verbose)

        out.warning(f"Restarting {service_name} server...")
        out.info("Note: This is a placeholder command.")
        out.info(
            "For production deployments, use your process manager to restart the service."
        )
