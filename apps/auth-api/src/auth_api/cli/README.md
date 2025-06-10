***REMOVED*** CLI Module

The CLI module provides a comprehensive command-line interface for the Auth API service. Built with Typer and Rich, it offers an intuitive and powerful way to manage the authentication service, perform administrative tasks, and monitor system health.

***REMOVED******REMOVED*** Overview

The CLI provides:

- **Service Management**: Start, stop, and configure the Auth API service
- **User Administration**: Create, manage, and monitor user accounts
- **Health Monitoring**: Check service and database health
- **Configuration Management**: View and validate service configuration
- **Development Tools**: Utilities for development and debugging

***REMOVED******REMOVED*** Architecture

***REMOVED******REMOVED******REMOVED*** Main Components

- **`main.py`** (10KB, 328 lines): Main CLI application and command orchestration
- **`utils.py`** (11KB, 339 lines): Shared utilities, helpers, and common functions
- **`commands/`**: Individual command modules
  - **`users.py`** (18KB, 552 lines): User management commands
  - **`health.py`** (8.1KB, 293 lines): Health check commands

***REMOVED******REMOVED******REMOVED*** Technology Stack

- **Typer**: Modern CLI framework with type hints
- **Rich**: Beautiful terminal output with colors, tables, and progress bars
- **Async Support**: Full async/await support for database operations
- **Type Safety**: Comprehensive type hints throughout

***REMOVED******REMOVED*** Commands Overview

***REMOVED******REMOVED******REMOVED*** Server Management

```bash
***REMOVED*** Start the Auth API server
auth-api serve [OPTIONS]

Options:
  --host TEXT          Host to bind server to [default: 0.0.0.0]
  --port INTEGER       Port to bind server to [default: 8003]
  --reload             Enable auto-reload for development
  --log-level TEXT     Set log level (DEBUG, INFO, WARNING, ERROR)
  --verbose, -v        Enable verbose logging and output
  --quiet, -q          Suppress console output except errors
```

***REMOVED******REMOVED******REMOVED*** Configuration Management

```bash
***REMOVED*** Display current configuration
auth-api config [OPTIONS]

Options:
  --show-secrets       Show sensitive configuration values
  --verbose, -v        Show detailed configuration information
```

***REMOVED******REMOVED******REMOVED*** User Management

```bash
***REMOVED*** List users with filtering options
auth-api users list [OPTIONS]

***REMOVED*** Create new users
auth-api users create [OPTIONS]

***REMOVED*** User status management
auth-api users activate USER_EMAIL_OR_ID
auth-api users deactivate USER_EMAIL_OR_ID
auth-api users delete USER_EMAIL_OR_ID

***REMOVED*** User statistics and analytics
auth-api users stats [OPTIONS]
```

***REMOVED******REMOVED******REMOVED*** Health Monitoring

```bash
***REMOVED*** Comprehensive health checks
auth-api health check [OPTIONS]

***REMOVED*** Component-specific checks
auth-api health self [OPTIONS]
auth-api health database [OPTIONS]
```

***REMOVED******REMOVED******REMOVED*** Database Operations

```bash
***REMOVED*** Initialize database schema
auth-api init-db [OPTIONS]
```

***REMOVED******REMOVED*** Key Features

***REMOVED******REMOVED******REMOVED*** Rich Terminal Output

The CLI uses Rich for beautiful, informative output:

```python
***REMOVED*** Color-coded status messages
console.print("[green]✓[/green] User created successfully")
console.print("[red]✗[/red] Authentication failed")
console.print("[yellow]⚠[/yellow] Database connection slow")

***REMOVED*** Formatted tables for data display
table = Table(title="User Statistics")
table.add_column("Metric", style="cyan")
table.add_column("Value", style="magenta")
table.add_row("Total Users", str(total_users))
console.print(table)

***REMOVED*** Progress bars for long operations
with Progress() as progress:
    task = progress.add_task("Creating users...", total=100)
    ***REMOVED*** ... operation with progress updates
```

***REMOVED******REMOVED******REMOVED*** Async Database Operations

All database operations are fully async:

```python
@app.command()
async def create_user(
    email: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    admin: bool = False
) -> None:
    """Create a new user account."""
    try:
        user = await auth_service.create_user(email, username, password)
        console.print(f"[green]✓[/green] User created: {user.email}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(1)
```

***REMOVED******REMOVED******REMOVED*** Configuration Integration

Commands automatically integrate with the application configuration:

```python
***REMOVED*** Load configuration from environment
config = Config()

***REMOVED*** Override with command-line options
if auth_api_url:
    config.auth_api_url = auth_api_url

***REMOVED*** Use configuration in commands
response = await health_service.check_all()
```

***REMOVED******REMOVED******REMOVED*** Error Handling

Comprehensive error handling with user-friendly messages:

```python
try:
    result = await some_operation()
except DatabaseError as e:
    console.print(f"[red]Database Error:[/red] {e}")
    console.print("[yellow]Tip:[/yellow] Check your database connection")
    raise typer.Exit(1)
except ValidationError as e:
    console.print(f"[red]Validation Error:[/red] {e}")
    raise typer.Exit(1)
```

***REMOVED******REMOVED*** Main Modules

***REMOVED******REMOVED******REMOVED*** `main.py` - CLI Application Core

The main CLI application file that orchestrates all commands:

***REMOVED******REMOVED******REMOVED******REMOVED*** Key Features:

- **Command Registration**: Registers all command modules
- **Global Options**: Handles verbose/quiet modes
- **Environment Setup**: Initializes configuration and logging
- **Error Handling**: Global exception handling for CLI operations

***REMOVED******REMOVED******REMOVED******REMOVED*** Main Components:

```python
***REMOVED*** Main CLI app
app = typer.Typer(
    name="auth-api",
    help="Auth API CLI - Authentication service management tool",
    add_completion=False,
    rich_markup_mode="rich"
)

***REMOVED*** Command registration
app.add_typer(users_app, name="users")
app.add_typer(health_app, name="health")

***REMOVED*** Global commands
@app.command()
def serve(options...): pass

@app.command()
def config(options...): pass

@app.command()
def version(): pass
```

***REMOVED******REMOVED******REMOVED*** `utils.py` - Shared Utilities

Common utilities and helper functions used across all CLI commands:

***REMOVED******REMOVED******REMOVED******REMOVED*** Key Features:

- **Configuration Helpers**: Load and validate configuration
- **Database Utilities**: Database connection and initialization
- **Output Formatting**: Consistent terminal output formatting
- **Validation Helpers**: Input validation and sanitization
- **Error Handling**: Common error handling patterns

***REMOVED******REMOVED******REMOVED******REMOVED*** Main Functions:

```python
***REMOVED*** Configuration management
def load_config(verbose: bool = False) -> Config
def validate_config(config: Config) -> List[str]

***REMOVED*** Database operations
async def init_database(confirm: bool = True) -> bool
async def check_database_connection() -> bool

***REMOVED*** Output formatting
def format_user_table(users: List[User]) -> Table
def format_health_result(result: HealthCheckResult) -> Panel
def print_success(message: str) -> None
def print_error(message: str) -> None

***REMOVED*** Validation
def validate_email(email: str) -> bool
def validate_password(password: str) -> bool
def prompt_password() -> str
```

***REMOVED******REMOVED******REMOVED*** `commands/users.py` - User Management

Comprehensive user management commands:

***REMOVED******REMOVED******REMOVED******REMOVED*** Features:

- **User Creation**: Interactive and batch user creation
- **User Listing**: Filtered and paginated user lists
- **User Management**: Activate, deactivate, delete users
- **User Statistics**: Analytics and reporting
- **Bulk Operations**: Mass user operations

***REMOVED******REMOVED******REMOVED******REMOVED*** Commands:

```python
@users_app.command("list")
async def list_users(
    limit: int = 50,
    active_only: bool = False,
    search: Optional[str] = None,
    verbose: bool = False
) -> None: pass

@users_app.command("create")
async def create_user(
    email: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    admin: bool = False,
    verbose: bool = False
) -> None: pass

@users_app.command("stats")
async def user_stats(verbose: bool = False) -> None: pass
```

***REMOVED******REMOVED******REMOVED*** `commands/health.py` - Health Monitoring

Health check and monitoring commands:

***REMOVED******REMOVED******REMOVED******REMOVED*** Features:

- **Service Health**: Check Auth API service health
- **Database Health**: Monitor database connectivity and performance
- **Component Checks**: Individual component health verification
- **Performance Monitoring**: Response time tracking
- **Dependency Checks**: External service health verification

***REMOVED******REMOVED******REMOVED******REMOVED*** Commands:

```python
@health_app.command("check")
async def health_check(
    auth_api_url: Optional[str] = None,
    backend_api_url: Optional[str] = None,
    timeout: int = 5,
    verbose: bool = False
) -> None: pass

@health_app.command("self")
async def health_self(
    timeout: int = 5,
    verbose: bool = False
) -> None: pass

@health_app.command("database")
async def health_database(verbose: bool = False) -> None: pass
```

***REMOVED******REMOVED*** Development Patterns

***REMOVED******REMOVED******REMOVED*** Adding New Commands

1. **Create Command Module**: Add new file in `commands/` directory
2. **Define Command App**: Create Typer app for the command group
3. **Implement Commands**: Add individual command functions
4. **Register Commands**: Import and register in `main.py`
5. **Add Tests**: Write comprehensive tests for new commands

Example new command structure:

```python
***REMOVED*** commands/example.py
import typer
from rich.console import Console

app = typer.Typer(name="example", help="Example commands")
console = Console()

@app.command()
async def hello(name: str = typer.Option(..., help="Name to greet")) -> None:
    """Say hello to someone."""
    console.print(f"[green]Hello {name}![/green]")

@app.command()
async def goodbye(name: str) -> None:
    """Say goodbye to someone."""
    console.print(f"[blue]Goodbye {name}![/blue]")
```

***REMOVED******REMOVED******REMOVED*** Utility Functions

When adding utility functions to `utils.py`:

1. **Group by Function**: Related utilities together
2. **Type Hints**: Always include comprehensive type hints
3. **Error Handling**: Include proper error handling
4. **Documentation**: Add clear docstrings
5. **Testing**: Write unit tests for utilities

***REMOVED******REMOVED******REMOVED*** Command Options

Standard patterns for command options:

```python
@app.command()
async def example_command(
    ***REMOVED*** Required positional argument
    required_arg: str,

    ***REMOVED*** Optional argument with default
    optional_arg: Optional[str] = None,

    ***REMOVED*** Flag option
    flag: bool = typer.Option(False, "--flag", help="Enable flag"),

    ***REMOVED*** Option with validation
    count: int = typer.Option(1, min=1, max=100, help="Count (1-100)"),

    ***REMOVED*** Global options
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Quiet mode")
) -> None:
    """Example command with standard option patterns."""
    pass
```

***REMOVED******REMOVED*** Testing

***REMOVED******REMOVED******REMOVED*** CLI Testing Patterns

```python
import pytest
from typer.testing import CliRunner
from auth_api.cli.main import app

runner = CliRunner()

def test_command():
    result = runner.invoke(app, ["command", "arg"])
    assert result.exit_code == 0
    assert "expected output" in result.stdout

@pytest.mark.asyncio
async def test_async_command():
    ***REMOVED*** Test async CLI commands
    result = runner.invoke(app, ["users", "list"])
    assert result.exit_code == 0
```

***REMOVED******REMOVED******REMOVED*** Testing Guidelines

1. **Test All Commands**: Ensure all CLI commands have tests
2. **Test Error Cases**: Test both success and failure scenarios
3. **Mock Dependencies**: Mock database and external services
4. **Test Output**: Verify command output and formatting
5. **Test Options**: Test all command-line options and flags

***REMOVED******REMOVED*** Best Practices

***REMOVED******REMOVED******REMOVED*** Command Design

1. **Clear Names**: Use descriptive, intuitive command names
2. **Consistent Options**: Use consistent option patterns across commands
3. **Help Text**: Provide clear help text for all commands and options
4. **Validation**: Validate all input parameters
5. **Error Messages**: Provide actionable error messages

***REMOVED******REMOVED******REMOVED*** User Experience

1. **Progress Indicators**: Show progress for long-running operations
2. **Interactive Prompts**: Use prompts for sensitive operations
3. **Confirmation**: Require confirmation for destructive operations
4. **Output Formatting**: Use tables, colors, and formatting effectively
5. **Exit Codes**: Use appropriate exit codes for scripting

***REMOVED******REMOVED******REMOVED*** Performance

1. **Async Operations**: Use async/await for all I/O operations
2. **Lazy Loading**: Load resources only when needed
3. **Caching**: Cache frequently accessed data
4. **Pagination**: Implement pagination for large result sets
5. **Connection Pooling**: Use efficient database connections

***REMOVED******REMOVED*** Contributing

When contributing to the CLI module:

1. **Follow Patterns**: Use existing command patterns as templates
2. **Type Safety**: Include comprehensive type hints
3. **Documentation**: Update this README for significant changes
4. **Testing**: Add tests for all new commands and utilities
5. **User Experience**: Focus on intuitive, helpful user interfaces

***REMOVED******REMOVED*** Dependencies

The CLI module depends on:

- **Typer**: Modern CLI framework
- **Rich**: Terminal formatting and output
- **Asyncio**: Async operation support
- **Auth Services**: Authentication and health services
- **Configuration**: Application configuration system
