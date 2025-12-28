"""Extra tests to cover small branches in recommendation models."""

from __future__ import annotations

from recommendation_api.models.recommendation import MovieRecommendation


def test_movie_recommendation_handles_invalid_date_and_genres_string() -> None:
    class MovieLike:
        id = 1
        title = "T"
        release_date = "not-a-date"
        genres = "Drama"

    rec = MovieRecommendation.from_movie(MovieLike())
    assert rec.release_date is None
    assert rec.genres == ["Drama"]
