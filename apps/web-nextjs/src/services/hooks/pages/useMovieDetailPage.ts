"use client";

import { Movie } from "@/domain/entities";
import { useAuth } from "@/services/hooks";
import { MoviesAPI } from "@/services/api/movies/movies-api";
import { MovieDetailResponse, SimilarMovie } from "@/services/api/bff/types";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createLogger } from "@/utils/logging";
import { useMovieInteractions } from "@/services/hooks/domain/movie";
import { CacheKeys } from "@/services/cache";
import { useMemo } from "react";

// Create logger for this hook
const logger = createLogger("useMovieDetailPage");

/**
 * Hook for fetching and managing a single movie with complete detail data
 *
 * Enhanced with comprehensive cache integration:
 * - Uses centralized cache keys for consistency across the app
 * - Integrates with global cache management system
 * - Provides cache utilities for performance optimization
 * - Automatic prefetching of related data (cast, similar movies)
 * - Smart cache invalidation strategies
 * - Cross-hook cache coordination
 *
 * Features:
 * - Complete movie details from BFF API (includes user interactions, cast, similar movies, trailers)
 * - Optimistic updates for user interactions (watched, liked, watchlist)
 * - Intelligent caching with 5-minute stale time
 * - Background prefetching of related movie details
 * - Cache utilities for performance optimization
 * - Consistent API with other page hooks
 *
 * @param id - Movie ID to fetch
 * @returns Movie data, loading state, error, interaction functions, and cache utilities
 */
export function useMovieDetailPage(id: number) {
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();

  // Log hook initialization
  logger.debug(
    `useMovieDetailPage initialized with id: ${id}, authenticated: ${isAuthenticated}`
  );

  // Use centralized cache keys for consistency
  const queryKey = useMemo(() => CacheKeys.movies.detail(id), [id]);

  // Check if we have recent mutations that would make the cache fresh
  const queryMeta = queryClient.getQueryState(queryKey);
  const hasRecentMutation =
    queryMeta?.dataUpdatedAt && Date.now() - queryMeta.dataUpdatedAt < 10000; // 10 seconds

  // Fetch movie data from BFF (includes user interactions, cast, and similar movies)
  const {
    data: movieDetailResponse,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey,
    queryFn: () => {
      logger.debug(
        `🔄 useMovieDetailPage query function called for movie ${id}`,
        {
          hasExistingCache: !!queryClient.getQueryData(queryKey),
          hasRecentMutation,
          cacheAge: queryMeta?.dataUpdatedAt
            ? Date.now() - queryMeta.dataUpdatedAt
            : null,
        }
      );
      return MoviesAPI.getMovieDetail(id);
    },
    enabled: id > 0 && !hasRecentMutation, // Disable if we have fresh mutations
    staleTime: 1000 * 60 * 5, // 5 minutes - consistent with other hooks
    refetchOnWindowFocus: false, // Consistent with other hooks
    refetchOnMount: false, // Prevent automatic refetch on mount if we have cache
    notifyOnChangeProps: ["data", "error", "isLoading"],
    onSuccess: (response: MovieDetailResponse) => {
      logger.info("Loaded movie data from BFF", {
        movieId: id,
        title: response.data?.title,
        isWatched: response.context?.user_interactions?.is_watched,
        isFavorite: response.context?.user_interactions?.is_favorite,
        inWatchlist: response.context?.user_interactions?.in_watchlist,
        castCount: response.related?.cast?.length || 0,
        similarMoviesCount: response.related?.similar_movies?.length || 0,
        trailers: response.related?.trailers,
      });

      // Log similar movies data to help with debugging
      if (
        response.related?.similar_movies &&
        response.related.similar_movies.length > 0
      ) {
        logger.debug(
          `Received ${response.related.similar_movies.length} similar movies:`,
          {
            firstMovie: {
              id: response.related.similar_movies[0]?.id,
              title: response.related.similar_movies[0]?.title,
              similarityScore:
                response.related.similar_movies[0]?.similarity_score,
              reason: response.related.similar_movies[0]?.recommendation_reason,
            },
          }
        );
      }

      // Prefetch related movie details in background
      if (
        response.related?.similar_movies &&
        response.related.similar_movies.length > 0
      ) {
        const firstFewSimilar = response.related.similar_movies.slice(0, 3);
        firstFewSimilar.forEach((similarMovie: SimilarMovie) => {
          if (similarMovie.id) {
            const similarMovieKey = CacheKeys.movies.detail(similarMovie.id);
            if (!queryClient.getQueryData(similarMovieKey)) {
              logger.debug(
                `Prefetching similar movie: ${similarMovie.title} (${similarMovie.id})`
              );
              queryClient.prefetchQuery({
                queryKey: similarMovieKey,
                queryFn: () => MoviesAPI.getMovieDetail(similarMovie.id),
                staleTime: 1000 * 60 * 5,
              });
            }
          }
        });
      }
    },
    onError: (error: unknown) => {
      // Handle specific error types for better UX
      const apiError = error as { status?: number };
      if (apiError.status === 404) {
        logger.info(`Movie ${id} not found (404)`, { movieId: id });
      } else {
        logger.error(`Error loading movie ${id} from BFF:`, error);
      }
    },
  }) as {
    data: MovieDetailResponse | undefined;
    isLoading: boolean;
    error: unknown;
    refetch: () => void;
  };

  // Log errors
  if (error) {
    // Error logging is now handled in the component for better UX
    // This avoids duplicate logging while still providing context if needed
  }

  // Process similar movies data to include similarity scores and reasons
  const similarMovies = useMemo(() => {
    if (!movieDetailResponse?.related?.similar_movies) return [];

    return movieDetailResponse.related.similar_movies.map(
      (movie: SimilarMovie) => ({
        ...movie,
        // Ensure these fields are properly typed and accessible in the UI
        similarityScore: movie.similarity_score,
        recommendationReason: movie.recommendation_reason || "similar",
      })
    );
  }, [movieDetailResponse?.related?.similar_movies]);

  // Convert ResponseBuilder response to Movie with user interactions and cast
  // SIMPLIFIED: Just process the API response, no complex cache logic
  const movie: Movie | undefined = useMemo(() => {
    if (!movieDetailResponse) return undefined;

    const baseMovie = {
      // Use API response data as base
      ...movieDetailResponse.data,
      // Use API response interaction states as fallback values
      liked:
        movieDetailResponse.context?.user_interactions?.is_favorite || false,
      watched:
        movieDetailResponse.context?.user_interactions?.is_watched || false,
      in_watchlist:
        movieDetailResponse.context?.user_interactions?.in_watchlist || false,
      // Include cast data directly in the movie object
      cast: movieDetailResponse.related?.cast,
      // Include trailers data
      trailers: movieDetailResponse.related?.trailers,
      // Add user_interactions structure for useMovieInteractions hook consistency
      user_interactions: {
        is_watched:
          movieDetailResponse.context?.user_interactions?.is_watched || false,
        is_favorite:
          movieDetailResponse.context?.user_interactions?.is_favorite || false,
        in_watchlist:
          movieDetailResponse.context?.user_interactions?.in_watchlist || false,
      },
    } as unknown as Movie;

    logger.debug(`🎬 useMovieDetailPage processing movie data for ${id}`, {
      movieTitle: baseMovie.title,
      interactionStates: {
        liked: baseMovie.liked,
        watched: baseMovie.watched,
        in_watchlist: baseMovie.in_watchlist,
      },
    });

    return baseMovie;
  }, [movieDetailResponse, id]);

  // Use the movie interactions hook for toggle functionality
  const {
    toggleWatched,
    toggleLiked,
    toggleWatchlist,
    isLoading: mutationLoading,
    cache: interactionCache,
  } = useMovieInteractions({
    movieId: id,
    movie,
  });

  // Create wrapped toggle functions with proper error handling and logging
  const wrappedToggleWatched = useMemo(
    () => async () => {
      try {
        logger.debug(`Executing toggle watched for movie ${id}`);
        await toggleWatched(id);
        logger.debug(`Successfully toggled watched status for movie ${id}`);
      } catch (error) {
        logger.error(`Error toggling watched status for movie ${id}:`, error);
        throw error;
      }
    },
    [id, toggleWatched]
  );

  const wrappedToggleLiked = useMemo(
    () => async () => {
      try {
        logger.debug(`Executing toggle liked for movie ${id}`);
        await toggleLiked(id);
        logger.debug(`Successfully toggled liked status for movie ${id}`);
      } catch (error) {
        logger.error(`Error toggling liked status for movie ${id}:`, error);
        throw error;
      }
    },
    [id, toggleLiked]
  );

  const wrappedToggleWatchlist = useMemo(
    () => async () => {
      try {
        logger.debug(`Executing toggle watchlist for movie ${id}`);
        await toggleWatchlist(id);
        logger.debug(`Successfully toggled watchlist status for movie ${id}`);
      } catch (error) {
        logger.error(`Error toggling watchlist status for movie ${id}:`, error);
        throw error;
      }
    },
    [id, toggleWatchlist]
  );

  // Create optimistic update wrapper
  const updateMovieOptimistically = useMemo(
    () => (updatedMovie: Movie) => {
      interactionCache.updateMovieOptimistically(() => updatedMovie);
    },
    [interactionCache]
  );

  // Cache utilities - consistent with other page hooks
  const cache = useMemo(
    () => ({
      /**
       * Get the current cache key being used
       */
      getCacheKey: () => queryKey,

      /**
       * Invalidate all movie list queries (useful after movie interactions)
       * This ensures movie lists reflect updated interaction states
       */
      invalidateMovieLists: () => {
        logger.debug(`Invalidating movie lists after movie ${id} interactions`);
        return queryClient.invalidateQueries({
          predicate: (query) => {
            return (
              query.queryKey[0] === "movies" && query.queryKey[1] === "lists"
            );
          },
        });
      },

      /**
       * Prefetch movie details for performance (e.g., on hover)
       */
      prefetchMovieDetails: (movieId: number) => {
        const movieDetailsKey = CacheKeys.movies.detail(movieId);
        if (!queryClient.getQueryData(movieDetailsKey)) {
          logger.debug(`Prefetching movie details for ID: ${movieId}`);
          return queryClient.prefetchQuery({
            queryKey: movieDetailsKey,
            queryFn: () => MoviesAPI.getMovieDetail(movieId),
            staleTime: 1000 * 60 * 5,
          });
        }
      },

      /**
       * Prefetch all similar movies for this movie
       */
      prefetchSimilarMovies: () => {
        if (movieDetailResponse?.related?.similar_movies) {
          movieDetailResponse.related.similar_movies.forEach(
            (similarMovie: SimilarMovie) => {
              if (similarMovie.id) {
                cache.prefetchMovieDetails(similarMovie.id);
              }
            }
          );
        }
      },

      /**
       * Access to interaction cache utilities
       */
      interactions: interactionCache,

      /**
       * Get related movies data with similarity scores
       */
      getRelatedMovies: () => similarMovies,

      /**
       * Get cast data
       */
      getCast: () => movieDetailResponse?.related?.cast || [],
    }),
    [
      queryKey,
      queryClient,
      movieDetailResponse,
      id,
      interactionCache,
      similarMovies,
    ]
  );

  return {
    // Core data
    movie,
    isLoading,
    error,
    refetch,

    // Interaction functions
    toggleWatched: wrappedToggleWatched,
    toggleLiked: wrappedToggleLiked,
    toggleWatchlist: wrappedToggleWatchlist,
    mutationLoading, // Loading states for individual mutations

    // Related data (also available via cache utilities)
    relatedMovies: similarMovies,
    cast: movieDetailResponse?.related?.cast || [],

    // Enhanced cache integration
    cache,

    // Raw data for advanced usage
    rawData: movieDetailResponse,

    // Optimistic update functions
    updateMovieOptimistically,
  };
}
