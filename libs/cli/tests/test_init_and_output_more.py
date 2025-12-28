"""Extra unit tests to cover cli.__init__ lazy exports and CLIOutput branches."""

from __future__ import annotations

from unittest.mock import patch

import pytest


def test_cli_init_lazy_exports_and_dir() -> None:
    import cli

    ***REMOVED*** dir should include some known exports
    d = dir(cli)
    assert "CLIOutput" in d
    assert "validate_port" in d

    ***REMOVED*** lazy export resolution
    validate_port = cli.validate_port
    assert callable(validate_port)

    with pytest.raises(AttributeError):
        _ = cli.this_does_not_exist


def test_configure_basic_cli_logging_smoke() -> None:
    from cli.output.handler import configure_basic_cli_logging

    configure_basic_cli_logging(verbose=False, quiet=False, command_name="x")
    configure_basic_cli_logging(verbose=True, quiet=False, command_name="x")
    configure_basic_cli_logging(verbose=False, quiet=True, command_name="x")


def test_cli_output_confirm_and_progress_branches() -> None:
    from cli.output.handler import CLIOutput

    o = CLIOutput("x")

    ***REMOVED*** determinate progress
    p = o.progress("work", total=5)
    assert p.disable is not True

    ***REMOVED*** quiet confirm uses default
    oq = CLIOutput("x", quiet=True)
    assert oq.confirm("q?", default=True) is True

    with patch("cli.output.handler.Confirm.ask", return_value=False) as ask:
        assert o.confirm("q?", default=True) is False
        ask.assert_called_once()


def test_get_cli_output_factory() -> None:
    from cli.output.handler import get_cli_output

    out = get_cli_output("cmd", verbose=True, quiet=False)
    assert out.command_name == "cmd"
    assert out.verbose is True
