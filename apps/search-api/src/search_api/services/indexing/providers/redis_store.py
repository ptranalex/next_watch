"""Redis storage abstraction for suggestion indexing."""

import json
import re
from typing import Any

import redis.asyncio as redis


class RedisStore:
    """Encapsulates Redis operations used by the suggestion indexer."""

    def __init__(self, redis_url: str) -> None:
        self._client = redis.Redis.from_url(redis_url, decode_responses=True, encoding="utf-8")

    async def close(self) -> None:
        await self._client.close()

    async def clear_suggestions_and_entities(self) -> int:
        total_deleted = 0
        await self._client.delete("suggestions")
        cursor_sugg = 0
        cursor_entity = 0
        while True:
            cursor_sugg, keys = await self._client.scan(
                cursor=cursor_sugg, match="suggestions:*", count=1000
            )
            if keys:
                total_deleted += len(keys)
                await self._client.delete(*keys)

            cursor_entity, entity_keys = await self._client.scan(
                cursor=cursor_entity, match="entity:*", count=1000
            )
            if entity_keys:
                total_deleted += len(entity_keys)
                await self._client.delete(*entity_keys)

            if cursor_sugg == 0 and cursor_entity == 0:
                break
        return total_deleted

    async def index_movies(
        self,
        movies: list[dict[str, Any]],
        *,
        include_words: bool,
        min_word_length: int,
        batch_size: int,
    ) -> int:
        pipeline = self._client.pipeline()
        count = 0
        for i, movie in enumerate(movies):
            title = (movie.get("title") or "").lower()
            movie_id = movie.get("id")
            pipeline.zadd("suggestions", {title: 0})
            pipeline.set(f"suggestions:{title}", str(movie_id))
            pipeline.set(f"suggestions_meta:{title}", f"movie:{movie_id}")

            movie_data = {
                "id": movie.get("id"),
                "title": movie.get("title"),
                "type": "movie",
                "image_path": movie.get("poster_path"),
                "year": movie.get("release_year"),
                "popularity": movie.get("popularity"),
                "vote_average": movie.get("vote_average"),
                "original_title_format": movie.get("title"),
                "overview": movie.get("overview"),
                "release_date": movie.get("release_date"),
                "backdrop_url": movie.get("backdrop_url"),
                "imdb_rating": movie.get("imdb_rating"),
                "runtime": movie.get("runtime"),
                "genres": movie.get("genres", []),
                "tmdb_id": movie.get("tmdb_id"),
                "imdb_id": movie.get("imdb_id"),
            }
            pipeline.set(f"entity:movie:{title}", json.dumps(movie_data))
            pipeline.set(f"entity:id:{movie_id}", json.dumps(movie_data))

            if "(" in title and ")" in title:
                main_title = title.split("(")[0].strip()
                if main_title:
                    pipeline.zadd("suggestions", {main_title: 0})
                    pipeline.set(f"suggestions:{main_title}", str(movie_id))
                    pipeline.set(f"suggestions_meta:{main_title}", f"movie:{movie_id}")
                    pipeline.set(f"entity:movie:{main_title}", json.dumps(movie_data))
                for paren_part in re.findall(r"\((.*?)\)", title):
                    if paren_part and len(paren_part) > 3:
                        paren_title = paren_part.strip().lower()
                        pipeline.zadd("suggestions", {paren_title: 0})
                        pipeline.set(f"suggestions:{paren_title}", str(movie_id))
                        pipeline.set(f"suggestions_meta:{paren_title}", f"movie:{movie_id}")

            if include_words:
                words = re.split(r"[\s\(\)\[\]\{\}\:\;\,\.\-\_\+\=]+", title)
                for word in [w for w in words if w and len(w) >= min_word_length]:
                    pipeline.zadd("suggestions", {word: 0})
                    pipeline.set(f"suggestions:{word}", str(movie_id))
                    pipeline.set(f"suggestions_meta:{word}", f"movie:{movie_id}")
                    if len(word) >= 5:
                        for prefix_len in range(min_word_length, min(len(word), 6)):
                            prefix = word[:prefix_len]
                            pipeline.zadd("suggestions", {prefix: 0})
                            ***REMOVED*** only set mapping once if not exists
                            pipeline.setnx(f"suggestions:{prefix}", str(movie_id))
                            pipeline.setnx(f"suggestions_meta:{prefix}", f"movie:{movie_id}")

            count += 1
            if (i + 1) % batch_size == 0 or i == len(movies) - 1:
                await pipeline.execute()
                pipeline = self._client.pipeline()
        return count

    async def index_actors(self, actors: list[dict[str, Any]], *, batch_size: int) -> int:
        pipeline = self._client.pipeline()
        count = 0
        for i, actor in enumerate(actors):
            name = (actor.get("name") or "").lower()
            actor_id = actor.get("id")
            pipeline.zadd("suggestions", {name: 0})
            pipeline.set(f"suggestions:{name}", str(actor_id))
            pipeline.set(f"suggestions_meta:{name}", f"actor:{actor_id}")
            actor_data = {
                "id": actor.get("id"),
                "name": actor.get("name"),
                "type": "actor",
                "image_path": actor.get("profile_path"),
                "popularity": actor.get("popularity"),
                "gender": actor.get("gender"),
            }
            pipeline.set(f"entity:actor:{name}", json.dumps(actor_data))
            count += 1
            if (i + 1) % batch_size == 0 or i == len(actors) - 1:
                await pipeline.execute()
                pipeline = self._client.pipeline()
        return count

    async def counts(self) -> dict[str, int]:
        zset_count = await self._client.zcard("suggestions")
        cursor = 0
        entity_count = 0
        while True:
            cursor, keys = await self._client.scan(cursor=cursor, match="entity:*", count=1000)
            entity_count += len(keys)
            if cursor == 0:
                break
        return {"zset": int(zset_count), "entities": entity_count}
