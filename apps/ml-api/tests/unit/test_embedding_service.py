"""Unit tests for ML API EmbeddingService without downloading real models."""

from __future__ import annotations

import builtins
import sys
from types import ModuleType


class _FakeArray(list):
    def tolist(self):
        return list(self)


class _FakeModel:
    def __init__(self, dims: int = 3):
        self._dims = dims

    def get_sentence_embedding_dimension(self):
        return self._dims

    def encode(self, text: str):
        ***REMOVED*** Ensure the parameter is "used" (Ruff ARG002 in test stubs)
        _ = text
        return _FakeArray([1.0] * self._dims)


def _install_fake_sentence_transformers(monkeypatch, dims: int = 3):
    m = ModuleType("sentence_transformers")

    class SentenceTransformer:
        def __init__(self, model_name_or_path=None, cache_folder=None):
            ***REMOVED*** Store args so they are "used" (Ruff ARG002 in test stubs)
            self._model_name_or_path = model_name_or_path
            self._cache_folder = cache_folder
            self._model = _FakeModel(dims=dims)

        def get_sentence_embedding_dimension(self):
            return self._model.get_sentence_embedding_dimension()

        def encode(self, text: str):
            return self._model.encode(text)

    m.SentenceTransformer = SentenceTransformer
    monkeypatch.setitem(sys.modules, "sentence_transformers", m)


def test_get_instance_singleton() -> None:
    from ml_api.services.embedding_service import EmbeddingService

    a = EmbeddingService.get_instance()
    b = EmbeddingService.get_instance()
    assert a is b


def test_load_model_import_error_sets_unavailable(monkeypatch) -> None:
    from ml_api.services.embedding_service import EmbeddingService

    svc = EmbeddingService()

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "sentence_transformers":
            raise ImportError("nope")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    assert svc.load_model() is False
    info = svc.get_model_info()
    assert info["health"] == "unavailable"


def test_load_model_success_and_generate_embeddings(monkeypatch) -> None:
    dims = 4
    _install_fake_sentence_transformers(monkeypatch, dims=dims)

    from ml_api.services.embedding_service import EmbeddingService

    svc = EmbeddingService()
    assert svc.load_model() is True

    info = svc.get_model_info()
    assert info["status"] == "loaded"
    assert info["health"] == "ok"
    assert info["dimensions"] == dims

    m = svc.generate_movie_embedding("m1", "Title", "Overview", genres=["Drama"])
    assert m["dimensions"] == dims
    assert m["embedding"] == [1.0, 1.0, 1.0, 1.0]

    u = svc.generate_user_preference_vector("u1", watched_genres={"Drama": 1.0})
    assert u["dimensions"] == dims
    assert u["preference_vector"] == [1.0, 1.0, 1.0, 1.0]

    u0 = svc.generate_user_preference_vector("u2", watched_genres=None)
    assert u0["preference_vector"] == [0.0, 0.0, 0.0, 0.0]


def test_generate_movie_embedding_uses_mock_when_load_fails(monkeypatch) -> None:
    from ml_api.services.embedding_service import EmbeddingService

    svc = EmbeddingService()

    monkeypatch.setattr(svc, "load_model", lambda: False)

    res = svc.generate_movie_embedding("m1", "t", "o")
    assert res["model_id"].endswith("_mock")
    assert len(res["embedding"]) == int(res["dimensions"])
