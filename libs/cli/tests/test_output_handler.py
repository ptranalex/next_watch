"""Tests for CLIOutput handler functionality."""

from io import StringIO
from unittest.mock import Mock, patch

from cli.output.handler import CLIOutput

from tests.test_base import CLITestCase


class TestCLIOutput(CLITestCase):
    """Test cases for CLIOutput class."""

    def test_cli_output_initialization(self) -> None:
        """Test CLIOutput initialization with different modes."""
        ***REMOVED*** Standard mode
        output = CLIOutput("test-cmd")
        assert output.command_name == "test-cmd"
        assert output.verbose is False
        assert output.quiet is False

        ***REMOVED*** Verbose mode
        verbose_output = CLIOutput("test-cmd", verbose=True)
        assert verbose_output.verbose is True

        ***REMOVED*** Quiet mode
        quiet_output = CLIOutput("test-cmd", quiet=True)
        assert quiet_output.quiet is True

    @patch("cli.output.handler.CLIOutput.console")
    def test_info_output(self, mock_console: Mock) -> None:
        """Test info message output."""
        output = CLIOutput("test-cmd")
        output.console = mock_console

        output.info("Test info message")

        mock_console.print.assert_called_once()

    @patch("cli.output.handler.CLIOutput.console")
    def test_success_output(self, mock_console: Mock) -> None:
        """Test success message output."""
        output = CLIOutput("test-cmd")
        output.console = mock_console

        output.success("Operation completed!")

        mock_console.print.assert_called_once()

    @patch("cli.output.handler.CLIOutput.console")
    def test_warning_output(self, mock_console: Mock) -> None:
        """Test warning message output."""
        output = CLIOutput("test-cmd")
        output.console = mock_console

        output.warning("This is a warning")

        mock_console.print.assert_called_once()

    @patch("cli.output.handler.CLIOutput.error_console")
    def test_error_output(self, mock_error_console: Mock) -> None:
        """Test error message output."""
        output = CLIOutput("test-cmd")
        output.error_console = mock_error_console

        output.error("Something went wrong")

        mock_error_console.print.assert_called_once()

    @patch("cli.output.handler.CLIOutput.console")
    def test_quiet_mode_suppresses_output(self, mock_console: Mock) -> None:
        """Test that quiet mode suppresses standard output."""
        output = CLIOutput("test-cmd", quiet=True)
        output.console = mock_console

        output.info("This should be suppressed")
        output.success("This should be suppressed")
        output.warning("This should be suppressed")

        ***REMOVED*** Should not print in quiet mode
        mock_console.print.assert_not_called()

    @patch("cli.output.handler.CLIOutput.error_console")
    def test_quiet_mode_allows_errors(self, mock_error_console: Mock) -> None:
        """Test that quiet mode still allows error output."""
        output = CLIOutput("test-cmd", quiet=True)
        output.error_console = mock_error_console

        output.error("This should show")
        mock_error_console.print.assert_called_once()

    @patch("cli.output.handler.structlog")
    def test_log_operation_verbose_mode(self, mock_structlog: Mock) -> None:
        """Test operational logging in verbose mode."""
        mock_logger = Mock()
        mock_structlog.get_logger.return_value.bind.return_value = mock_logger

        output = CLIOutput("test-cmd", verbose=True)
        output.logger = mock_logger

        output.log_operation("Test operation", key="value", count=42)

        ***REMOVED*** Should log the operation with structured data
        mock_logger.info.assert_called_once_with("Test operation", key="value", count=42)

    @patch("cli.output.handler.structlog")
    def test_log_operation_non_verbose_mode(self, mock_structlog: Mock) -> None:
        """Test that operational logging is suppressed in non-verbose mode."""
        mock_logger = Mock()
        mock_structlog.get_logger.return_value.bind.return_value = mock_logger

        output = CLIOutput("test-cmd", verbose=False)
        output.logger = mock_logger

        output.log_operation("Test operation", key="value")

        ***REMOVED*** Should not log in non-verbose mode
        mock_logger.info.assert_not_called()

    @patch("cli.output.handler.structlog")
    def test_log_error(self, mock_structlog: Mock) -> None:
        """Test error logging."""
        mock_logger = Mock()
        mock_structlog.get_logger.return_value.bind.return_value = mock_logger

        output = CLIOutput("test-cmd")
        output.logger = mock_logger
        exception = ValueError("Test error")

        output.log_error("Operation failed", exception, context="test")

        ***REMOVED*** Should always log errors regardless of verbose mode
        mock_logger.error.assert_called_once_with(
            "Operation failed",
            error=str(exception),
            error_type=type(exception).__name__,
            context="test",
        )

    def test_progress_quiet_mode(self) -> None:
        """Test progress indicator in quiet mode."""
        output = CLIOutput("test-cmd", quiet=True)

        progress = output.progress("Processing...")

        ***REMOVED*** In quiet mode, should return disabled progress
        assert progress.disable is True

    def test_progress_normal_mode(self) -> None:
        """Test progress indicator in normal mode."""
        output = CLIOutput("test-cmd", verbose=False, quiet=False)

        progress = output.progress("Processing...")

        ***REMOVED*** In normal mode, should return enabled progress
        assert progress.disable is not True


class TestCLIOutputIntegration(CLITestCase):
    """Integration tests for CLIOutput with real Rich console."""

    def test_real_console_integration(self) -> None:
        """Test CLIOutput with a real Rich console."""
        from rich.console import Console

        ***REMOVED*** Create a console that writes to a StringIO for testing
        string_io = StringIO()
        console = Console(file=string_io, width=80)

        output = CLIOutput("test-cmd")
        output.console = console

        ***REMOVED*** Test different output types
        output.info("Information message")
        output.success("Success message")
        output.warning("Warning message")

        ***REMOVED*** Get the output and verify content is present
        console_output = string_io.getvalue()

        assert "Information message" in console_output
        assert "Success message" in console_output
        assert "Warning message" in console_output

    def test_error_console_integration(self) -> None:
        """Test error console with real Rich console."""
        from rich.console import Console

        string_io = StringIO()
        error_console = Console(file=string_io, width=80)

        output = CLIOutput("test-cmd")
        output.error_console = error_console

        output.error("Error message")

        console_output = string_io.getvalue()
        assert "Error message" in console_output

    def test_console_properties(self) -> None:
        """Test that CLIOutput has the expected console properties."""
        output = CLIOutput("test-cmd")

        ***REMOVED*** Should have console and error_console attributes
        assert hasattr(output, "console")
        assert hasattr(output, "error_console")
        assert hasattr(output, "logger")

        ***REMOVED*** Should have the expected methods
        assert hasattr(output, "info")
        assert hasattr(output, "success")
        assert hasattr(output, "warning")
        assert hasattr(output, "error")
        assert hasattr(output, "log_operation")
        assert hasattr(output, "log_error")
        assert hasattr(output, "progress")
