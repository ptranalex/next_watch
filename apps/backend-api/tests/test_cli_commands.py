from typer.testing import CliRunner


def test_cli_db_migrate_command_exists() -> None:
    # Importing the app should register commands (side-effect import in backend_api.cli).
    from backend_api.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["db", "--help"])

    assert result.exit_code == 0
    assert "migrate" in result.stdout


