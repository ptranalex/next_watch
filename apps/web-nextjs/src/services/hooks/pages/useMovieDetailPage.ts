"use client";

import { Movie } from "@/domain/entities";
import { useAuth } from "@/services/hooks";
import { MoviesAPI } from "@/services/api/movies/movies-api";
import { MovieDetailData } from "@/services/api/bff/types";
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

  // Fetch movie data from BFF (includes user interactions, cast, and similar movies)
  const {
    data: movieDetailData,
    isLoading,
    error,
    refetch,
  } = useQuery<MovieDetailData>({
    queryKey,
    queryFn: () => MoviesAPI.getMovieDetail(id),
    enabled: id > 0,
    staleTime: 1000 * 60 * 5, // 5 minutes - consistent with other hooks
    refetchOnWindowFocus: false, // Consistent with other hooks
    notifyOnChangeProps: ["data", "error", "isLoading"],
    onSuccess: (data) => {
      logger.info("Loaded movie data from BFF", {
        movieId: id,
        title: data.movie.title,
        isWatched: data.user_interactions?.is_watched,
        isFavorite: data.user_interactions?.is_favorite,
        inWatchlist: data.user_interactions?.in_watchlist,
        castCount: data.cast?.length || 0,
        similarMoviesCount: data.similar_movies?.length || 0,
        trailers: data.trailers,
      });

      // Prefetch related movie details in background
      if (data.similar_movies && data.similar_movies.length > 0) {
        const firstFewSimilar = data.similar_movies.slice(0, 3);
        firstFewSimilar.forEach((similarMovie) => {
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
    onError: (error) => {
      logger.error(`Error loading movie ${id} from BFF:`, error);
    },
  });

  // Log errors
  if (error) {
    logger.error(`Error in useMovieDetailPage hook for movie ${id}:`, error);
  }

  // Convert MovieDetailData to Movie with user interactions and cast
  const movie: Movie | undefined = movieDetailData
    ? ({
        ...movieDetailData.movie,
        // Map BFF user interactions to Movie properties
        liked: movieDetailData.user_interactions?.is_favorite || false,
        watched: movieDetailData.user_interactions?.is_watched || false,
        in_watchlist: movieDetailData.user_interactions?.in_watchlist || false,
        // Include cast data directly in the movie object
        cast: movieDetailData.cast,
        // Include trailers data
        trailers: movieDetailData.trailers,
      } as Movie)
    : undefined;

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
        if (movieDetailData?.similar_movies) {
          movieDetailData.similar_movies.forEach((similarMovie) => {
            if (similarMovie.id) {
              cache.prefetchMovieDetails(similarMovie.id);
            }
          });
        }
      },

      /**
       * Access to interaction cache utilities
       */
      interactions: interactionCache,

      /**
       * Get related movies data
       */
      getRelatedMovies: () => movieDetailData?.similar_movies || [],

      /**
       * Get cast data
       */
      getCast: () => movieDetailData?.cast || [],
    }),
    [queryKey, queryClient, movieDetailData, id, interactionCache]
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
    relatedMovies: movieDetailData?.similar_movies || [],
    cast: movieDetailData?.cast || [],

    // Enhanced cache integration
    cache,

    // Raw data for advanced usage
    rawData: movieDetailData,

    // Optimistic update functions
    updateMovieOptimistically,
  };
}
