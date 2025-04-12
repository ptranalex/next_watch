"""Utility functions for the CLI interface."""

import logging
import os
import re
from typing import Any, Dict, Tuple

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

logger = logging.getLogger(__name__)


def display_config(console: Console, command: str, config: Dict[str, Any]) -> None:
    """Display configuration settings.

    Args:
        console: Rich console instance
        command: Name of the command being executed
        config: Configuration settings dictionary
    """
    console.print(f"\n[bold blue]Configuration for '{command}' command:[/bold blue]")

    ***REMOVED*** Filter out sensitive information
    filtered_config = {
        k: v for k, v in config.items() if "token" not in k and "key" not in k
    }

    ***REMOVED*** Handle sensitive values
    for key in config:
        if "token" in key or "key" in key:
            if config[key] and len(str(config[key])) > 0:
                filtered_config[key] = "********"
            else:
                filtered_config[key] = "[red]Not set[/red]"

    ***REMOVED*** Display configuration
    for key, value in filtered_config.items():
        if key in ["verbose", "quiet", "cache_enabled"]:
            value = "[green]Enabled[/green]" if value else "[grey]Disabled[/grey]"
        console.print(f"  [cyan]{key}[/cyan]: {value}")

    console.print("")


def ensure_ha_connection(
    console: Console, ha_url: str, ha_token: str
) -> Tuple[str, str]:
    """Ensure Home Assistant connection settings are available.

    If URL or token are missing, prompt the user to enter them interactively
    and validate the connection.

    Args:
        console: Rich console instance
        ha_url: Home Assistant URL
        ha_token: Home Assistant access token

    Returns:
        Tuple of (ha_url, ha_token), updated with user input or environment variables
    """
    ***REMOVED*** Check URL
    if not ha_url:
        env_url = os.getenv("HA_URL")
        if env_url:
            ha_url = env_url
            console.print(
                "[yellow]No Home Assistant URL provided, using environment variable.[/yellow]"
            )
        else:
            console.print(
                "\n[blue]Home Assistant URL is required but not found.[/blue]"
            )
            console.print("You can press Ctrl+C to cancel.")

            try:
                ***REMOVED*** Prompt for URL with a default suggestion
                url_default = "http://homeassistant.local:8123"
                if os.path.exists("/etc/avahi/services/homeassistant.service"):
                    ***REMOVED*** If running on same machine as Home Assistant
                    url_default = "http://localhost:8123"

                new_url = Prompt.ask(
                    "Enter your Home Assistant URL", default=url_default
                )

                ***REMOVED*** Basic URL validation
                url_pattern = re.compile(
                    r"^(http|https)://"  ***REMOVED*** http:// or https://
                    r"([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])"  ***REMOVED*** domain
                    r"(\.[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])*"  ***REMOVED*** domain
                    r"(:\d+)?"  ***REMOVED*** optional port
                    r"(/.*)?$"  ***REMOVED*** optional path
                )

                if not url_pattern.match(new_url):
                    console.print(
                        "[yellow]Warning: The URL format looks incorrect. Make sure it includes http:// or https://[/yellow]"
                    )
                    if Confirm.ask("Use this URL anyway?", default=False):
                        ha_url = new_url
                    else:
                        console.print("[yellow]URL entry canceled.[/yellow]")
                        raise KeyboardInterrupt()
                else:
                    ha_url = new_url

                ***REMOVED*** Set environment variable for current process
                os.environ["HA_URL"] = ha_url

                ***REMOVED*** Provide instructions for permanent storage
                console.print(
                    "\n[blue]To save this URL permanently, run this command in your terminal:[/blue]"
                )
                console.print(f"  export HA_URL='{ha_url}'")
                console.print(
                    "[blue]Add the above line to your shell profile (~/.bashrc, ~/.zshrc, etc.) to make it permanent.[/blue]"
                )

            except KeyboardInterrupt:
                console.print("\n[yellow]URL entry canceled.[/yellow]")
                raise

    ***REMOVED*** Check token
    if not ha_token:
        env_token = os.getenv("HA_TOKEN")
        if env_token:
            ha_token = env_token
            console.print(
                "[yellow]No Home Assistant token provided, using environment variable.[/yellow]"
            )
        else:
            console.print(
                "\n[blue]Home Assistant access token is required but not found.[/blue]"
            )
            console.print("You can press Ctrl+C to cancel.")
            console.print(
                "[blue]You can generate a long-lived access token in Home Assistant:[/blue]"
            )
            console.print(
                "  1. Go to your profile in Home Assistant (click on your username)"
            )
            console.print("  2. Scroll down to 'Long-Lived Access Tokens'")
            console.print("  3. Create a new token and copy it")

            try:
                ***REMOVED*** Prompt for token (hidden input)
                new_token = Prompt.ask(
                    "Enter your Home Assistant access token", password=True
                )

                ***REMOVED*** Basic token validation - typically HA tokens are long
                if len(new_token) < 20:
                    console.print(
                        "[yellow]Warning: The token seems too short. Home Assistant tokens are typically longer.[/yellow]"
                    )
                    if not Confirm.ask("Use this token anyway?", default=False):
                        console.print("[yellow]Token entry canceled.[/yellow]")
                        raise KeyboardInterrupt()

                ha_token = new_token

                ***REMOVED*** Set environment variable for current process
                os.environ["HA_TOKEN"] = ha_token

                ***REMOVED*** Provide instructions for permanent storage
                console.print(
                    "\n[blue]To save this token permanently, run this command in your terminal:[/blue]"
                )
                console.print(f"  export HA_TOKEN='{ha_token}'")
                console.print(
                    "[blue]Add the above line to your shell profile (~/.bashrc, ~/.zshrc, etc.) to make it permanent.[/blue]"
                )

            except KeyboardInterrupt:
                console.print("\n[yellow]Token entry canceled.[/yellow]")
                raise

    ***REMOVED*** Validate connection if we have both URL and token
    if ha_url and ha_token:
        ***REMOVED*** Import here to avoid circular imports
        from ha_assistant.hass.client import HomeAssistantClient

        console.print("[blue]Validating Home Assistant connection...[/blue]")
        client = HomeAssistantClient(ha_url, ha_token)

        try:
            ***REMOVED*** Use async_run to execute the async validation
            import asyncio

            async def validate_connection() -> Tuple[bool, str]:
                """Validate the Home Assistant connection.

                Returns:
                    Tuple of (is_valid, error_message)
                """
                try:
                    ***REMOVED*** Try to fetch API status to validate connection
                    message = {"type": "get_config", "id": client.get_next_id()}
                    await client.send_message_async(message)
                    return True, ""
                except Exception as e:
                    return False, str(e)

            ***REMOVED*** Create a new event loop for validation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            is_valid, error_msg = loop.run_until_complete(validate_connection())
            loop.close()

            if is_valid:
                console.print(
                    "[green]✓ Connection to Home Assistant successful[/green]"
                )
            else:
                console.print(f"[red]✗ Connection failed: {error_msg}[/red]")
                if not Confirm.ask("Continue anyway?", default=False):
                    console.print(
                        "[yellow]Operation canceled due to connection failure.[/yellow]"
                    )
                    raise typer.Exit(1)

        except Exception as e:
            console.print(f"[red]Error validating connection: {str(e)}[/red]")
            if not Confirm.ask("Continue anyway?", default=False):
                console.print(
                    "[yellow]Operation canceled due to validation error.[/yellow]"
                )
                raise typer.Exit(1)

    return ha_url, ha_token
