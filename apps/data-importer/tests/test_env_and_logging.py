"""Unit tests for env loading helpers and logging configuration."""

from __future__ import annotations

import builtins
import sys
from pathlib import Path
from types import ModuleType

import pytest


def test_find_project_root_marker_found(tmp_path: Path) -> None:
    from data_importer.config.env import find_project_root

    ***REMOVED*** create a marker at root
    (tmp_path / "pyproject.toml").write_text("x")

    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)

    assert find_project_root(nested) == tmp_path


def test_find_project_root_fallback_and_raise(tmp_path: Path, monkeypatch) -> None:
    import data_importer.config.env as env

    ***REMOVED*** fallback: fake __file__ to a deep path under tmp
    deep = tmp_path / "a" / "b" / "c" / "d" / "env.py"
    deep.parent.mkdir(parents=True)
    monkeypatch.setattr(env, "__file__", str(deep))

    ***REMOVED*** start in a directory with no markers
    start = tmp_path / "a" / "b" / "c" / "d"
    assert env.find_project_root(start) == tmp_path / "a"

    ***REMOVED*** raise: point __file__ to non-existent tree
    monkeypatch.setattr(
        env, "__file__", str(tmp_path / "doesnotexist" / "a" / "b" / "c" / "d" / "env.py")
    )
    with pytest.raises(FileNotFoundError):
        env.find_project_root(start)


def test_load_environment_variables_import_error(monkeypatch) -> None:
    from data_importer.config.env import load_environment_variables

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "dotenv":
            raise ImportError("no")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    assert load_environment_variables(project_root=None) is False


def test_load_environment_variables_processes_env_files(tmp_path: Path, monkeypatch) -> None:
    import data_importer.config.env as env

    calls = []

    m = ModuleType("dotenv")

    def load_dotenv(dotenv_path=None, override=False):
        calls.append((Path(dotenv_path).name, override))

    m.load_dotenv = load_dotenv
    monkeypatch.setitem(sys.modules, "dotenv", m)

    (tmp_path / ".env").write_text("A=1")
    (tmp_path / ".env.local").write_text("A=2")

    assert env.load_environment_variables(project_root=tmp_path) is True
    assert (".env", False) in calls
    assert (".env.local", True) in calls


def test_env_getters(monkeypatch) -> None:
    from data_importer.config.env import get_env_bool, get_env_int, get_env_var

    monkeypatch.delenv("X_REQ", raising=False)
    with pytest.raises(ValueError):
        get_env_var("X_REQ", required=True)

    monkeypatch.setenv("BOOL1", "true")
    assert get_env_bool("BOOL1") is True

    monkeypatch.setenv("INT1", "not-int")
    assert get_env_int("INT1", default=7) == 7


def test_configure_logging_and_decorator(tmp_path: Path) -> None:
    from data_importer.config.logging import configure_logging, with_logging

    log_dir = tmp_path / "logs"
    configure_logging(log_level="DEBUG", log_dir=log_dir, verbose=True, quiet=False)

    ***REMOVED*** should create at least one log file
    assert any(
        p.name.startswith("data_importer_") and p.suffix == ".log" for p in log_dir.iterdir()
    )

    @with_logging(log_level="INFO", log_dir=None, verbose=False, quiet=True)
    def f():
        return "ok"

    assert f() == "ok"
