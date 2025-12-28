"""Unit tests for Recommendation API Pydantic models."""

from __future__ import annotations

from datetime import date

import pytest


def test_movie_models_construct() -> None:
    from recommendation_api.models.movie import Movie, MovieMetadata, MovieVector

    md = MovieMetadata(id=1, title="A", genres=["Drama"])
    vec = MovieVector(
        movie_id=1, vector=[0.1, 0.2], vector_type="content", model_version="v1", created_at="now"
    )
    movie = Movie(metadata=md, content_vector=vec)

    assert movie.metadata.id == 1
    assert movie.content_vector is not None


def test_user_models_construct() -> None:
    from recommendation_api.models.user import UserPreferences, UserProfile

    prefs = UserPreferences(user_id=10, favorite_genres=["Drama"], min_rating=7.0)
    profile = UserProfile(user_id=10, preferences=prefs, watch_history=[1, 2])

    assert profile.preferences.min_rating == 7.0


def test_movie_recommendation_from_movie_parses_date_and_genres() -> None:
    from recommendation_api.models.recommendation import MovieRecommendation

    class Genre:
        def __init__(self, name: str):
            self.name = name

    class MovieLike:
        id = 123
        title = "Test"
        overview = "O"
        release_date = "2020-01-02"
        genres = [Genre("Drama"), "Comedy"]
        imdb_rating = 7.0
        tmdb_rating = 8.0
        poster_path = "x"

    rec = MovieRecommendation.from_movie(MovieLike(), reason="because", score=0.9)
    assert rec.id == 123
    assert rec.release_date == date(2020, 1, 2)
    assert rec.genres == ["Drama", "Comedy"]


def test_movie_recommendation_from_movie_requires_id() -> None:
    from recommendation_api.models.recommendation import MovieRecommendation

    class Bad:
        id = None

    with pytest.raises(ValueError):
        MovieRecommendation.from_movie(Bad())
