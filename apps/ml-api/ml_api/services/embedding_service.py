"""Service for generating embeddings using sentence-transformers."""

import logging
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar, Union, cast

from ml_api.config import config

logger = logging.getLogger(__name__)

***REMOVED*** Type hint for SentenceTransformer
***REMOVED*** Define a type alias that works at runtime and for static type checking
if TYPE_CHECKING:
    ***REMOVED*** Only used during type checking
    from sentence_transformers import SentenceTransformer as STModel
else:
    ***REMOVED*** Runtime behavior - try to import or use Any as fallback
    try:
        from sentence_transformers import SentenceTransformer as STModel
    except ImportError:
        STModel = Any


class EmbeddingService:
    """Service for generating embeddings using sentence-transformers."""

    _instance = None
    _model: Optional[Any] = None
    _model_info: Dict[str, Any] = {
        "model_id": config.embedding_model,
        "dimensions": 384,  ***REMOVED*** Default for all-MiniLM-L6-v2
        "version": "1.0.0",
        "status": "not_loaded",
        "health": "unknown",
        "stats": {
            "requests_processed": 0,
            "average_processing_time_ms": 0,
        },
    }

    @classmethod
    def get_instance(cls) -> "EmbeddingService":
        """Get or create the singleton instance of EmbeddingService."""
        if cls._instance is None:
            cls._instance = EmbeddingService()
        return cls._instance

    def __init__(self) -> None:
        """Initialize the embedding service."""
        self._total_processing_time = 0.0

    def load_model(self) -> bool:
        """Load the sentence-transformer model.

        Returns:
            bool: True if the model was loaded successfully, False otherwise.
        """
        if self._model is not None:
            logger.info("Model already loaded")
            return True

        try:
            ***REMOVED*** Lazy import to avoid loading heavy dependencies until needed
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading model: {config.embedding_model}")
            model_kwargs: Dict[str, Any] = {}

            if config.model_cache_dir:
                model_kwargs["cache_folder"] = str(config.model_cache_dir)

            start_time = time.time()
            ***REMOVED*** Pass model_kwargs as keyword arguments to avoid type errors
            self._model = SentenceTransformer(
                model_name_or_path=config.embedding_model,
                cache_folder=model_kwargs.get("cache_folder"),
            )
            load_time = time.time() - start_time

            ***REMOVED*** Update model info
            self._model_info["status"] = "loaded"
            self._model_info["health"] = "ok"
            self._model_info["dimensions"] = self._model.get_sentence_embedding_dimension()

            logger.info(f"Model loaded successfully in {load_time:.2f}s")
            return True

        except ImportError:
            logger.error(
                "sentence-transformers not installed. "
                "Install with 'pip install sentence-transformers'"
            )
            self._model_info["status"] = "error"
            self._model_info["health"] = "unavailable"
            return False

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._model_info["status"] = "error"
            self._model_info["health"] = "error"
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model.

        Returns:
            Dict[str, Any]: Information about the model.
        """
        return self._model_info

    def generate_movie_embedding(
        self,
        movie_id: str,
        title: str,
        overview: str,
        genres: Optional[List[str]] = None,
        additional_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate an embedding for a movie.

        Args:
            movie_id: Unique identifier for the movie.
            title: Movie title.
            overview: Movie overview/description.
            genres: List of movie genres.
            additional_metadata: Additional movie metadata.

        Returns:
            Dict[str, Any]: Dictionary with movie_id, embedding, model_id, and dimensions.
        """
        ***REMOVED*** Ensure model is loaded
        if not self._model and not self.load_model():
            ***REMOVED*** If model loading failed, return a zero vector
            logger.warning(
                f"Using mock embedding for movie {movie_id} due to model loading failure"
            )
            return self._generate_mock_embedding(movie_id)

        ***REMOVED*** Prepare text for embedding
        text_to_embed = f"{title}. {overview}"

        if genres:
            text_to_embed += f" Genres: {', '.join(genres)}"

        ***REMOVED*** Generate embedding
        start_time = time.time()
        embedding = cast(Any, self._model).encode(text_to_embed).tolist()
        processing_time = time.time() - start_time

        ***REMOVED*** Update stats
        self._update_stats(processing_time)

        logger.debug(f"Generated embedding for movie {movie_id} in {processing_time*1000:.2f}ms")

        return {
            "movie_id": movie_id,
            "embedding": embedding,
            "model_id": self._model_info["model_id"],
            "dimensions": self._model_info["dimensions"],
        }

    def generate_user_preference_vector(
        self,
        user_id: str,
        liked_movies: Optional[List[Dict[str, Union[str, float]]]] = None,
        watched_genres: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Generate a preference vector for a user.

        Args:
            user_id: Unique identifier for the user.
            liked_movies: Movies liked by the user with ratings.
            watched_genres: Genres watched by the user with preference weights.

        Returns:
            Dict[str, Any]: Dictionary with user_id, preference_vector, model_id, and dimensions.
        """
        ***REMOVED*** Ensure model is loaded
        if not self._model and not self.load_model():
            ***REMOVED*** If model loading failed, return a zero vector
            logger.warning(
                f"Using mock preference vector for user {user_id} due to model loading failure"
            )
            return self._generate_mock_user_vector(user_id)

        ***REMOVED*** In a real implementation, we would:
        ***REMOVED*** 1. Generate embeddings for each liked movie
        ***REMOVED*** 2. Weight them by the user's rating
        ***REMOVED*** 3. Combine them with genre preferences
        ***REMOVED*** 4. Normalize the resulting vector

        ***REMOVED*** For this example, we'll just create a simple representation
        ***REMOVED*** based on the genres the user watches

        ***REMOVED*** This is a simplified approach - in a real system, this would be more sophisticated
        if watched_genres:
            genres_text = " ".join(
                [f"{genre} " * int(weight * 10) for genre, weight in watched_genres.items()]
            )

            start_time = time.time()
            preference_vector = cast(Any, self._model).encode(genres_text).tolist()
            processing_time = time.time() - start_time

            ***REMOVED*** Update stats
            self._update_stats(processing_time)

            logger.debug(
                f"Generated preference vector for user {user_id} in {processing_time*1000:.2f}ms"
            )
        else:
            ***REMOVED*** If no genre preferences, return a zero vector
            dimensions = int(self._model_info["dimensions"])
            preference_vector = [0.0] * dimensions
            logger.debug(
                f"Generated zero preference vector for user {user_id} (no genre preferences)"
            )

        return {
            "user_id": user_id,
            "preference_vector": preference_vector,
            "model_id": self._model_info["model_id"],
            "dimensions": self._model_info["dimensions"],
        }

    def _generate_mock_embedding(self, movie_id: str) -> Dict[str, Any]:
        """Generate a mock embedding for testing or when the model is unavailable.

        Args:
            movie_id: Unique identifier for the movie.

        Returns:
            Dict[str, Any]: Dictionary with movie_id, embedding, model_id, and dimensions.
        """
        ***REMOVED*** Generate a zero vector with the expected dimensions
        dimensions = int(self._model_info["dimensions"])
        embedding = [0.0] * dimensions

        return {
            "movie_id": movie_id,
            "embedding": embedding,
            "model_id": f"{self._model_info['model_id']}_mock",
            "dimensions": dimensions,
        }

    def _generate_mock_user_vector(self, user_id: str) -> Dict[str, Any]:
        """Generate a mock user preference vector for testing or when the model is unavailable.

        Args:
            user_id: Unique identifier for the user.

        Returns:
            Dict[str, Any]: Dictionary with user_id, preference_vector, model_id, and dimensions.
        """
        ***REMOVED*** Generate a zero vector with the expected dimensions
        dimensions = int(self._model_info["dimensions"])
        preference_vector = [0.0] * dimensions

        return {
            "user_id": user_id,
            "preference_vector": preference_vector,
            "model_id": f"{self._model_info['model_id']}_mock",
            "dimensions": dimensions,
        }

    def _update_stats(self, processing_time: float) -> None:
        """Update the statistics for the embedding service.

        Args:
            processing_time: Time taken to process the request in seconds.
        """
        ***REMOVED*** Update the total processing time
        self._total_processing_time += processing_time

        ***REMOVED*** Update the number of requests processed
        stats = cast(Dict[str, Any], self._model_info["stats"])
        stats["requests_processed"] += 1

        ***REMOVED*** Update the average processing time
        avg_time = (self._total_processing_time * 1000) / stats["requests_processed"]
        stats["average_processing_time_ms"] = round(avg_time, 2)


***REMOVED*** Create a default instance
embedding_service = EmbeddingService.get_instance()
