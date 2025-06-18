"""NextWatch CLI Utilities.

Production-ready command-line interface utilities for the NextWatch platform,
providing consistent UX, enterprise patterns, and operational excellence.
"""

***REMOVED*** Core output and CLI utilities
from .output.handler import CLIOutput, get_cli_output, configure_basic_cli_logging

***REMOVED*** Configuration display and management
from .config.display import print_config, create_config_command
from .config.masking import mask_url_credentials

***REMOVED*** Service interaction framework
from .services.service_registry import ServiceRegistry, ServiceConfig
from .services.client_factory import ServiceClientFactory

***REMOVED*** Health check utilities
from .health.display import display_health_results
from .health.generators import create_health_commands

***REMOVED*** Command generators
from .commands.generators.cache import create_cache_commands
from .commands.generators.service import (
    create_service_commands,
    create_database_commands,
)
from .commands.generators.version import (
    create_version_command,
    create_simple_version_command,
)
from .commands.generators.serve import (
    create_serve_command,
    create_serve_app,
)

***REMOVED*** Async utilities
from .async_utils.lifecycle import ServiceLifecycleManager
from .async_utils.concurrency import (
    run_concurrently,
    gather_with_timeout,
    run_with_retries,
)
from .async_utils.context import with_timeout, with_progress, async_context_manager

***REMOVED*** Logging framework (Phase 3)
from .logging.setup import get_logger
from .logging.structured import CLILogger, with_logging, get_cli_logger
from .logging.formatters import COLOR_THEMES

***REMOVED*** Utilities (Phase 3)
from .utils.validation import (
    ValidationError,
    validate_url,
    validate_port,
    validate_timeout,
)
from .utils.async_helpers import run_async_command, AsyncCommandRunner
from .utils.security import mask_url, mask_sensitive_value, is_sensitive_field

__version__ = "0.3.0"

__all__ = [
    ***REMOVED*** Core output
    "CLIOutput",
    "get_cli_output",
    ***REMOVED*** Configuration
    "print_config",
    "create_config_command",
    "mask_url_credentials",
    ***REMOVED*** Services
    "ServiceRegistry",
    "ServiceConfig",
    "ServiceClientFactory",
    ***REMOVED*** Health
    "display_health_results",
    "create_health_commands",
    ***REMOVED*** Command generators
    "create_cache_commands",
    "create_service_commands",
    "create_database_commands",
    "create_version_command",
    "create_simple_version_command",
    "create_serve_command",
    "create_serve_app",
    ***REMOVED*** Async utilities
    "ServiceLifecycleManager",
    "run_concurrently",
    "gather_with_timeout",
    "run_with_retries",
    "with_timeout",
    "with_progress",
    "async_context_manager",
    ***REMOVED*** Logging (Phase 3)
    "configure_basic_cli_logging",
    "get_logger",
    "CLILogger",
    "with_logging",
    "get_cli_logger",
    "COLOR_THEMES",
    ***REMOVED*** Utilities (Phase 3)
    "ValidationError",
    "validate_url",
    "validate_port",
    "validate_timeout",
    "run_async_command",
    "AsyncCommandRunner",
    "mask_url",
    "mask_sensitive_value",
    "is_sensitive_field",
    ***REMOVED*** Version
    "__version__",
]
