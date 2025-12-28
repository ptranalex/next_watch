"""Environment variable loading with hierarchical .env file support."""

import os
from pathlib import Path

from config.env.discovery import find_project_root


class EnvironmentLoader:
    """Hierarchical environment variable loader."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or find_project_root()
        self.loaded_files: list[str] = []

    def load_environment(self, environment: str | None = None) -> dict[str, str]:
        """Load environment variables in hierarchical order."""
        if environment is None:
            environment = os.getenv("ENVIRONMENT", "development")

        env_files = [
            self.project_root / ".env",
            self.project_root / f".env.{environment}",
            self.project_root / ".env.local",
        ]

        loaded_vars = {}
        self.loaded_files = []

        for env_file in env_files:
            if env_file.exists():
                file_vars = self._load_env_file(env_file)
                loaded_vars.update(file_vars)
                self.loaded_files.append(env_file.name)

        return loaded_vars

    def _load_env_file(self, env_file: Path) -> dict[str, str]:
        """Load a single .env file."""
        try:
            from dotenv import dotenv_values

            values = dotenv_values(env_file)
            ***REMOVED*** Filter out None values and ensure all values are strings
            return {k: str(v) for k, v in values.items() if v is not None}
        except ImportError:
            return self._parse_env_file_manual(env_file)

    def _parse_env_file_manual(self, env_file: Path) -> dict[str, str]:
        """Manually parse a .env file."""
        env_vars = {}
        try:
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("***REMOVED***"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip().strip("\"'")
        except Exception as e:
            print(f"Error reading {env_file}: {e}")
        return env_vars


def load_environment_for_service(
    service_name: str,
    environment: str | None = None,
    project_root: Path | None = None,
) -> dict[str, str]:
    """Load environment for a service."""
    loader = EnvironmentLoader(project_root)
    env_vars = loader.load_environment(environment)

    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value

    return env_vars
