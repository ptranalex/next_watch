"""NextWatch CLI Utilities.

Production-ready command-line interface utilities for the NextWatch platform,
providing consistent UX, enterprise patterns, and operational excellence.
"""

***REMOVED*** Core output and CLI utilities
from .async_utils.concurrency import (
    gather_with_timeout,
    run_concurrently,
    run_with_retries,
)
from .async_utils.context import async_context_manager, with_progress, with_timeout

***REMOVED*** Async utilities
from .async_utils.lifecycle import ServiceLifecycleManager

***REMOVED*** Command generators
from .commands.generators.cache import create_cache_commands
from .commands.generators.serve import (
    create_serve_app,
    create_serve_command,
)
from .commands.generators.service import (
    create_database_commands,
    create_service_commands,
)
from .commands.generators.version import (
    create_simple_version_command,
    create_version_command,
)

***REMOVED*** Configuration display and management
from .config.display import create_config_command, print_config
from .config.masking import mask_url_credentials

***REMOVED*** Health check utilities
from .health.display import display_health_results
from .health.generators import create_health_commands
from .logging.formatters import COLOR_THEMES

***REMOVED*** Logging framework (Phase 3)
from .logging.setup import get_logger
from .logging.structured import CLILogger, get_cli_logger, with_logging
from .output.handler import CLIOutput, configure_basic_cli_logging, get_cli_output
from .services.client_factory import ServiceClientFactory

***REMOVED*** Service interaction framework
from .services.service_registry import ServiceConfig, ServiceRegistry
from .utils.async_helpers import AsyncCommandRunner, run_async_command
from .utils.security import is_sensitive_field, mask_sensitive_value, mask_url

***REMOVED*** Utilities (Phase 3)
from .utils.validation import (
    ValidationError,
    validate_port,
    validate_timeout,
    validate_url,
)

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
