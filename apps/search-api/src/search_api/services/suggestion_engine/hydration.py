"""
Entity hydration and enrichment for search suggestions.

This module handles fetching and enriching entity data for suggestions.
"""

import json
from typing import Any

from config.logging import get_logger

from .utils import build_image_url

logger = get_logger(__name__)


class EntityHydrator:
    """
    Handles entity data fetching and enrichment for suggestions.
    """

    def __init__(
        self,
        suggestion_key_prefix: str = "suggestions:",
        entity_key_prefix: str = "entity:",
        entity_types: list[str] | None = None,
    ):
        """
        Initialize the entity hydrator.

        Args:
            suggestion_key_prefix: Redis key prefix for suggestions
            entity_key_prefix: Redis key prefix for entities
            entity_types: List of entity types to search
        """
        self._suggestion_key_prefix = suggestion_key_prefix
        self._entity_key_prefix = entity_key_prefix
        self._entity_types = entity_types or ["movie", "actor", "director"]

    async def hydrate_suggestions(
        self, redis_client: Any, suggestions: list[str], limit: int
    ) -> list[dict[str, Any]]:
        """
        Convert suggestion strings to detailed entity objects using batch hydrations.

        Args:
            redis_client: Redis client instance
            suggestions: List of suggestion strings
            limit: Maximum number of results to return

        Returns:
            List of hydrated suggestion objects
        """
        detailed_suggestions = []
        seen_ids: set[int] = set()

        # Step 1: fetch meta (type:id) in batch, fallback to id-only
        meta_keys = [f"suggestions_meta:{s}" for s in suggestions]
        id_keys = [f"{self._suggestion_key_prefix}{s}" for s in suggestions]
        pipeline = redis_client.pipeline()
        for k in meta_keys:
            pipeline.get(k)
        for k in id_keys:
            pipeline.get(k)
        meta_results, id_results = [], []
        try:
            res = await pipeline.execute()
            meta_results = res[: len(meta_keys)]
            id_results = res[len(meta_keys) :]
        except Exception:
            # If pipeline fails, fall back to sequential gets (rare)
            meta_results = [await redis_client.get(k) for k in meta_keys]
            id_results = [await redis_client.get(k) for k in id_keys]

        # Resolve type and id per suggestion
        types: list[str | None] = []
        ids: list[int | None] = []
        for meta_val, id_val in zip(meta_results, id_results, strict=False):
            t, vid = None, None
            if meta_val and isinstance(meta_val, str) and ":" in meta_val:
                try:
                    t, id_str = meta_val.split(":", 1)
                    vid = int(id_str)
                except Exception:
                    t, vid = None, None
            if vid is None and id_val:
                try:
                    vid = int(id_val.decode() if isinstance(id_val, bytes) else id_val)
                    if t is None:
                        t = "movie"  # default
                except Exception:
                    vid = None
            types.append(t)
            ids.append(vid)

        # Step 2: batch fetch entities by id
        id_to_entity: dict[int, dict[str, Any]] = {}
        to_fetch_ids = [vid for vid in ids if isinstance(vid, int)]
        if to_fetch_ids:
            pipeline = redis_client.pipeline()
            for vid in to_fetch_ids:
                pipeline.get(f"entity:id:{vid}")
            id_entities = await pipeline.execute()
            for vid, raw in zip(to_fetch_ids, id_entities, strict=False):
                if raw:
                    try:
                        id_to_entity[vid] = json.loads(raw)
                    except Exception:
                        continue

        # Step 3: for unresolved, try entity by name in batch
        unresolved_names = [
            s
            for s, vid in zip(suggestions, ids, strict=False)
            if not (isinstance(vid, int) and vid in id_to_entity)
        ]
        name_map: dict[str, dict[str, Any]] = {}
        if unresolved_names:
            pipeline = redis_client.pipeline()
            name_keys = []
            for s in unresolved_names:
                for e_type in ["movie", "actor", "director"]:
                    k = f"{self._entity_key_prefix}{e_type}:{s}"
                    name_keys.append((s, e_type, k))
                    pipeline.get(k)
            name_entities = await pipeline.execute()
            for (s, e_type, _), raw in zip(name_keys, name_entities, strict=False):
                if s in name_map:
                    continue
                if raw:
                    try:
                        data = json.loads(raw)
                        data["type"] = e_type
                        name_map[s] = data
                    except Exception:
                        pass

        # Build final hydrated objects
        for s, t, vid in zip(suggestions, types, ids, strict=False):
            entity_data = None
            entity_type = t
            if isinstance(vid, int) and vid in id_to_entity:
                entity_data = id_to_entity[vid]
                entity_type = entity_type or entity_data.get("type", "movie")
            elif s in name_map:
                entity_data = name_map[s]
                entity_type = entity_type or entity_data.get("type", "movie")
            else:
                # fallback minimal
                entity_data = {
                    "title": s,
                    "type": entity_type or "movie",
                    "id": vid or (hash(s) % 100000),
                    "image_path": None,
                    "year": None,
                    "popularity": 0.0,
                }

            suggestion_obj = self._build_suggestion_object(s, entity_type, entity_data)

            entity_id = suggestion_obj.get("id")
            if entity_id is not None and entity_id in seen_ids:
                continue
            if entity_id is not None:
                seen_ids.add(entity_id)
            detailed_suggestions.append(suggestion_obj)
            if len(detailed_suggestions) >= limit:
                break

        return detailed_suggestions

    async def hydrate_extra_suggestions(
        self,
        redis_client: Any,
        extra_candidates: list[str],
        suggestion_texts_seen: set[str],
        seen_ids: set[int],
        limit: int,
    ) -> list[dict[str, Any]]:
        """
        Hydrate extra suggestion candidates into detailed entity objects.

        Args:
            redis_client: Redis client instance
            extra_candidates: List of extra suggestion candidates
            suggestion_texts_seen: Set of already seen suggestion texts
            seen_ids: Set of already seen entity IDs
            limit: Maximum number of results to return

        Returns:
            List of hydrated suggestion objects
        """
        detailed_suggestions = []

        for sugg in extra_candidates:
            if sugg in suggestion_texts_seen:
                continue
            suggestion_texts_seen.add(sugg)

            # Hydrate the extra suggestion into detailed entity object
            suggestion_key = f"{self._suggestion_key_prefix}{sugg}"
            movie_id = await redis_client.get(suggestion_key)

            entity_data = None
            entity_type = None

            if movie_id:
                try:
                    movie_id_int = int(
                        movie_id.decode() if isinstance(movie_id, bytes) else movie_id
                    )
                    entity_by_id_key = f"entity:id:{movie_id_int}"
                    id_data_json = await redis_client.get(entity_by_id_key)
                    if id_data_json:
                        try:
                            entity_data = json.loads(id_data_json)
                            entity_type = entity_data.get("type", "movie")
                        except json.JSONDecodeError:
                            pass
                except (ValueError, TypeError):
                    pass

            if entity_data is None:
                for e_type in ["movie", "actor", "director"]:
                    entity_key = f"{self._entity_key_prefix}{e_type}:{sugg}"
                    data_json = await redis_client.get(entity_key)
                    if data_json:
                        try:
                            entity_data = json.loads(data_json)
                            entity_type = e_type
                            break
                        except json.JSONDecodeError:
                            pass

            if entity_data is None:
                continue

            suggestion_obj = self._build_suggestion_object(sugg, entity_type, entity_data)

            entity_id = suggestion_obj.get("id")
            if entity_id is not None and entity_id in seen_ids:
                continue
            if entity_id is not None:
                seen_ids.add(entity_id)

            detailed_suggestions.append(suggestion_obj)
            if len(detailed_suggestions) >= limit:
                break

        return detailed_suggestions

    def _build_suggestion_object(
        self, text: str, entity_type: str | None, entity_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Build a suggestion object from entity data.

        Args:
            text: Suggestion text
            entity_type: Entity type
            entity_data: Raw entity data

        Returns:
            Structured suggestion object
        """
        suggestion_obj = {
            "text": entity_data.get("title", entity_data.get("name", text)),
            "type": entity_type or entity_data.get("type", "movie"),
            "id": entity_data.get("id", 0),
            "image_path": entity_data.get("poster_url")
            or entity_data.get("image_path")
            or entity_data.get("profile_path"),
            "year": entity_data.get("release_year")
            or entity_data.get("year")
            or entity_data.get("birth_year"),
            "popularity": entity_data.get("popularity", 0.0),
            "additional_info": {
                key: value
                for key, value in entity_data.items()
                if key not in ["text", "type", "id", "image_path", "year", "popularity"]
            },
        }

        # Build complete image URL
        suggestion_obj["image_path"] = build_image_url(suggestion_obj["image_path"])

        return suggestion_obj
