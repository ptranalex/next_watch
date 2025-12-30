"""Tests for data-importer configuration."""

from data_importer.config.app import Config


def test_config_singleton() -> None:
    c1 = Config.get_instance()
    c2 = Config.get_instance()
    assert c1 is c2


def test_config_defaults_are_reasonable() -> None:
    cfg = Config.get_instance()

    assert cfg.movie_sync_start_year > 1900
    assert cfg.movie_sync_end_year >= cfg.movie_sync_start_year
    assert cfg.movie_sync_limit_per_year > 0
    assert cfg.movie_sync_min_vote_count >= 0
    assert cfg.movie_sync_sort_by in {"popularity.desc", "vote_count.desc"}


def test_config_str_masks_secrets() -> None:
    from data_importer.config.app import Config

    cfg = Config(tmdb_access_token="abcd1234", imdb_api_key="wxyz9876", omdb_api_key="zzzz9999")
    s = str(cfg)
    # should not show full secrets
    assert "abcd1234" not in s
    assert "wxyz9876" not in s
    assert "zzzz9999" not in s
    # should keep last 4 chars
    assert "1234" in s
    assert "9876" in s
    assert "9999" in s
