"use client";

import { Movie } from "@/domain/entities";
import { deleteData, putData } from "@/services/api";
import { MovieDetailData } from "@/services/api/bff/types";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createLogger } from "@/utils/logging";
import { useAnalytics } from "@/services/hooks/core";
import { CacheKeys, CacheKeyUtils } from "@/services/cache";
import { useGlobalCacheManager } from "@/services/cache";

const logger = createLogger("useMovieInteractions");

interface UseMovieInteractionsOptions {
  movieId: number;
  movie?: Movie;
  additionalInvalidateKeys?: string[];
}

interface InteractionConfig {
  endpoint: string;
  currentValue: boolean;
  cacheKey: keyof MovieDetailData["user_interactions"];
  logName: string;
}

/**
 * Hook for managing movie interactions (watched, liked, watchlist) with optimistic updates
 * Enhanced with cache integration:
 * - Uses centralized cache keys for consistency
 * - Global cache manager integration for advanced operations
 * - Optimistic updates with automatic rollback on error
 * - Smart invalidation strategies
 * - Cache utilities for performance optimization
 *
 * Features:
 * - Immediate UI feedback with optimistic updates
 * - Automatic cache synchronization across all movie lists
 * - Error handling with rollback to previous state
 * - Performance optimizations with cache warming
 * - Flexible invalidation strategies (immediate, debounced, background)
 *
 * @param options - Configuration including movieId, movie data, and additional cache keys
 * @returns Interaction functions, loading states, and cache utilities
 */
export function useMovieInteractions({
  movieId,
  movie,
  additionalInvalidateKeys = [],
}: UseMovieInteractionsOptions) {
  const queryClient = useQueryClient();
  const globalCache = useGlobalCacheManager();
  const analytics = useAnalytics();

  // Helper function to update cache optimistically using centralized cache keys
  const updateCache = (
    updateFn: (data: MovieDetailData) => MovieDetailData
  ) => {
    const movieDetailKey = CacheKeys.movies.detail(movieId);
    queryClient.setQueryData<MovieDetailData>(movieDetailKey, (oldData) => {
      if (!oldData) return oldData;
      return updateFn(oldData);
    });
  };

  // Helper function to optimistically update movie lists
  const updateMovieListsCache = (updateFn: (movie: Movie) => Movie) => {
    // Update all queries that might contain this movie using CacheKeyUtils
    queryClient.setQueriesData(
      {
        predicate: (query) => {
          // Skip the current movie detail query to avoid conflicts
          if (
            CacheKeyUtils.isMovieKey(query.queryKey) &&
            CacheKeyUtils.extractMovieId(query.queryKey) === movieId
          ) {
            return false;
          }

          // Use CacheKeyUtils to identify movie list queries
          return CacheKeyUtils.isMovieListKey(query.queryKey);
        },
      },
      (oldData: unknown) => {
        if (!oldData) return oldData;

        // Handle infinite query data structure
        if (oldData && typeof oldData === "object" && "pages" in oldData) {
          const infiniteData = oldData as { pages: unknown[] };
          return {
            ...infiniteData,
            pages: infiniteData.pages.map((page: unknown) => {
              if (page && typeof page === "object") {
                // Handle actor page structure: { movies: { results: Movie[] } }
                if ("movies" in page) {
                  const actorPageData = page as {
                    movies?: { results?: Movie[] };
                  };
                  if (actorPageData.movies?.results) {
                    logger.debug(
                      `Updating actor page data structure for movie ${movieId} (found ${actorPageData.movies.results.length} movies)`
                    );
                    return {
                      ...page,
                      movies: {
                        ...actorPageData.movies,
                        results: actorPageData.movies.results.map(
                          (movie: Movie) =>
                            movie.id === movieId ? updateFn(movie) : movie
                        ),
                      },
                    };
                  }
                }
                // Handle regular page structure: { results: Movie[] }
                else if ("results" in page) {
                  const pageData = page as { results?: Movie[] };
                  if (pageData.results) {
                    logger.debug(
                      `Updating regular page data structure for movie ${movieId} (found ${pageData.results.length} movies)`
                    );
                  }
                  return {
                    ...pageData,
                    results:
                      pageData.results?.map((movie: Movie) =>
                        movie.id === movieId ? updateFn(movie) : movie
                      ) || pageData.results,
                  };
                }
              }
              return page;
            }),
          };
        }

        // Handle regular query data structure
        if (oldData && typeof oldData === "object" && "results" in oldData) {
          const queryData = oldData as { results: Movie[] };
          return {
            ...queryData,
            results: queryData.results.map((movie: Movie) =>
              movie.id === movieId ? updateFn(movie) : movie
            ),
          };
        }

        // Handle direct movie array
        if (Array.isArray(oldData)) {
          return oldData.map((movie: Movie) =>
            movie.id === movieId ? updateFn(movie) : movie
          );
        }

        return oldData;
      }
    );
  };

  // Helper function to invalidate related caches using global cache utilities
  const invalidateRelatedCaches = () => {
    // Use global cache manager for consistent invalidation
    globalCache.invalidateMovieRelatedQueries(movieId, "background");

    // Invalidate additional keys
    additionalInvalidateKeys.forEach((key) => {
      queryClient.invalidateQueries({ queryKey: [key] });
    });
  };

  // Helper function to create mutation configuration
  const createMutationConfig = (config: InteractionConfig) => ({
    mutationFn: async () => {
      if (!movie) throw new Error("Movie not loaded");

      logger.debug(
        `Toggling ${config.logName} for movie ${movieId}: ${
          config.currentValue
        } -> ${!config.currentValue}`
      );

      if (config.currentValue) {
        await deleteData(config.endpoint);
      } else {
        await putData(config.endpoint, {});
      }
    },
    onMutate: async () => {
      // Cancel outgoing refetches using centralized cache key
      const movieDetailKey = CacheKeys.movies.detail(movieId);
      await queryClient.cancelQueries({ queryKey: movieDetailKey });

      // Snapshot previous value
      const previousData =
        queryClient.getQueryData<MovieDetailData>(movieDetailKey);

      // Optimistically update movie detail cache
      updateCache((oldData) => {
        const newState = !oldData.user_interactions[config.cacheKey];
        logger.debug(
          `Optimistic update: ${config.logName} ${
            oldData.user_interactions[config.cacheKey]
          } -> ${newState} for movie ${movieId}`
        );

        return {
          ...oldData,
          user_interactions: {
            ...oldData.user_interactions,
            [config.cacheKey]: newState,
          },
        };
      });

      // Optimistically update movie lists cache
      updateMovieListsCache((movie) => {
        const newState = !config.currentValue;
        logger.debug(
          `Optimistic update movie lists: ${config.logName} ${config.currentValue} -> ${newState} for movie ${movieId}`
        );

        return {
          ...movie,
          [config.cacheKey === "is_watched"
            ? "watched"
            : config.cacheKey === "is_favorite"
            ? "liked"
            : config.cacheKey === "in_watchlist"
            ? "in_watchlist"
            : config.cacheKey]: newState,
        };
      });

      return { previousData };
    },
    onError: (
      err: Error,
      _variables: unknown,
      context: { previousData?: MovieDetailData } | undefined
    ) => {
      logger.error(
        `Failed to toggle ${config.logName} for movie ${movieId}:`,
        err
      );

      // Rollback using centralized cache key
      if (context?.previousData) {
        logger.debug(
          `Rolling back ${config.logName} to previous state for movie ${movieId}`
        );
        const movieDetailKey = CacheKeys.movies.detail(movieId);
        queryClient.setQueryData(movieDetailKey, context.previousData);
      }

      // Invalidate caches on error to ensure fresh data
      invalidateRelatedCaches();
    },
    onSuccess: () => {
      logger.info(
        `Successfully toggled ${config.logName} for movie ${movieId}`
      );

      // Track analytics event
      const action = config.currentValue
        ? config.cacheKey === "is_watched"
          ? "unmark_watched"
          : config.cacheKey === "is_favorite"
          ? "unlike"
          : "remove_from_watchlist"
        : config.cacheKey === "is_watched"
        ? "mark_watched"
        : config.cacheKey === "is_favorite"
        ? "like"
        : "add_to_watchlist";

      analytics.trackMovie(action, movieId, movie?.title?.toString());
    },
    onSettled: () => {
      // Do not invalidate caches on success since we have optimistic updates
      // Only invalidate on error (handled in onError)
    },
  });

  // Create the three mutations using useMutation at the top level
  const toggleWatched = useMutation(
    createMutationConfig({
      endpoint: `/bff/v1/user/interactions/movies/${movieId}/watched`,
      currentValue: movie?.watched ?? false,
      cacheKey: "is_watched",
      logName: "watched",
    })
  );

  const toggleLiked = useMutation(
    createMutationConfig({
      endpoint: `/bff/v1/user/interactions/movies/${movieId}/liked`,
      currentValue: movie?.liked ?? false,
      cacheKey: "is_favorite",
      logName: "liked",
    })
  );

  const toggleWatchlist = useMutation(
    createMutationConfig({
      endpoint: `/bff/v1/user/interactions/movies/${movieId}/watchlist`,
      currentValue: movie?.in_watchlist ?? false,
      cacheKey: "in_watchlist",
      logName: "watchlist",
    })
  );

  // Cache utilities for advanced usage
  const cache = {
    /**
     * Get the movie detail cache key
     */
    getMovieDetailKey: () => CacheKeys.movies.detail(movieId),

    /**
     * Invalidate all movie-related queries
     */
    invalidateMovieQueries: (
      strategy: "immediate" | "debounced" | "background" = "debounced"
    ) => {
      return globalCache.invalidateMovieRelatedQueries(movieId, strategy);
    },

    /**
     * Update movie optimistically in all caches
     */
    updateMovieOptimistically: (updateFn: (movie: Movie) => Movie) => {
      return globalCache.updateMovieOptimistically(movieId, updateFn);
    },

    /**
     * Warm related caches for better performance
     */
    warmRelatedCaches: () => {
      return globalCache.warmRelatedCaches(movieId);
    },

    /**
     * Manual cache cleanup
     */
    cleanupStaleData: () => {
      return globalCache.cleanupStaleMovieData();
    },
  };

  return {
    toggleWatched: toggleWatched.mutateAsync,
    toggleLiked: toggleLiked.mutateAsync,
    toggleWatchlist: toggleWatchlist.mutateAsync,
    isLoading: {
      watched: toggleWatched.isLoading,
      liked: toggleLiked.isLoading,
      watchlist: toggleWatchlist.isLoading,
    },

    // Cache utilities for advanced usage
    cache,

    // Raw mutation objects for advanced control
    mutations: {
      toggleWatched,
      toggleLiked,
      toggleWatchlist,
    },
  };
}
