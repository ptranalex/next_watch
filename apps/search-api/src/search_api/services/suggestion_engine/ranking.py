"""
Ranking and scoring algorithms for search suggestions.

This module contains the ranking logic for suggestions.
"""

from typing import Any, Dict, List, Tuple

from config.logging import get_logger

logger = get_logger(__name__)


class SuggestionRanker:
    """
    Handles ranking and scoring of search suggestions.
    """

    @staticmethod
    def sort_suggestions(
        suggestions: List[Dict[str, Any]], query_prefix: str
    ) -> List[Dict[str, Any]]:
        """
        Sort suggestions by relevance (exact matches first, then by score).

        Args:
            suggestions: List of suggestion objects
            query_prefix: The original query prefix

        Returns:
            Sorted list of suggestions
        """

        def sort_key(sugg: Dict[str, Any]) -> Tuple[int, float]:
            ***REMOVED*** Exact matches should be prioritized
            if sugg["text"] == query_prefix:
                return (0, sugg.get("popularity", 0) or 0)
            ***REMOVED*** Then prioritize by how closely the text starts with the query
            elif sugg["text"].startswith(query_prefix):
                return (1, sugg.get("popularity", 0) or 0)
            ***REMOVED*** Then suggestions where the query is a word in the text
            elif f" {query_prefix}" in f" {sugg['text']} ":
                return (2, sugg.get("popularity", 0) or 0)
            ***REMOVED*** Finally by default popularity/score
            else:
                return (3, sugg.get("popularity", 0) or 0)

        suggestions.sort(key=sort_key, reverse=True)
        return suggestions

    @staticmethod
    def enhance_with_search_metadata(
        suggestions: List[Dict[str, Any]], query: str
    ) -> List[Dict[str, Any]]:
        """
        Enhance suggestions with search metadata.

        Args:
            suggestions: List of suggestion objects
            query: The original search query

        Returns:
            Enhanced list of suggestions
        """
        for sugg in suggestions:
            if "search_type" not in sugg:
                sugg["search_type"] = (
                    "exact" if sugg["text"].lower().startswith(query.lower()) else "partial"
                )
            if "is_partial" not in sugg:
                sugg["is_partial"] = not sugg["text"].lower().startswith(query.lower())

        return suggestions

    @staticmethod
    def merge_unique_suggestions(
        primary_suggestions: List[Dict[str, Any]],
        additional_suggestions: List[Dict[str, Any]],
        limit: int,
        mark_additional_as_fuzzy: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Merge additional suggestions with primary ones, ensuring uniqueness.

        Args:
            primary_suggestions: Primary suggestion list
            additional_suggestions: Additional suggestions to merge
            limit: Maximum total suggestions
            mark_additional_as_fuzzy: Whether to mark additional suggestions as fuzzy

        Returns:
            Merged list of unique suggestions
        """
        merged = primary_suggestions.copy()
        existing_texts = {s["text"].lower() for s in merged}

        for sugg in additional_suggestions:
            if sugg["text"].lower() not in existing_texts:
                if mark_additional_as_fuzzy:
                    sugg["is_partial"] = True
                    sugg["search_type"] = "fuzzy"
                merged.append(sugg)
                existing_texts.add(sugg["text"].lower())
                if len(merged) >= limit:
                    break

        return merged[:limit]
