"use client";

import { Movie } from "@/domain/entities";
import { deleteData, postData } from "@/services/api";
import {
  MovieDetailData,
  MovieDetailResponse,
  SimilarMovie,
} from "@/services/api/bff/types";
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
  addEndpoint: string;
  removeEndpoint: string;
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
    updateFn: (
      data: MovieDetailData | MovieDetailResponse
    ) => MovieDetailData | MovieDetailResponse
  ) => {
    const movieDetailKey = CacheKeys.movies.detail(movieId);
    queryClient.setQueryData(movieDetailKey, (oldData: unknown) => {
      if (!oldData) return oldData;

      // Handle different response formats (legacy MovieDetailData vs new ResponseBuilder format)
      const typedData = oldData as MovieDetailData | MovieDetailResponse;
      if ("data" in typedData && "context" in typedData) {
        // New ResponseBuilder format: { data: Movie, context: { user_interactions: ... }, ... }
        console.log("🔄 UPDATING ResponseBuilder FORMAT");
        return updateFn(typedData);
      } else if ("movie" in typedData && "user_interactions" in typedData) {
        // Legacy MovieDetailData format: { movie: Movie, user_interactions: ... }
        console.log("🔄 UPDATING Legacy FORMAT");
        return updateFn(typedData);
      } else {
        console.log("🔄 UPDATING Unknown FORMAT", oldData);
        return updateFn(typedData);
      }
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

      console.log("🔧 MUTATION START:", {
        logName: config.logName,
        movieId,
        currentValue: config.currentValue,
        newValue: !config.currentValue,
        movie: {
          watched: movie.watched,
          liked: movie.liked,
          in_watchlist: movie.in_watchlist,
        },
      });

      logger.debug(
        `Toggling ${config.logName} for movie ${movieId}: ${
          config.currentValue
        } -> ${!config.currentValue}`
      );

      if (config.currentValue) {
        await deleteData(config.removeEndpoint);
      } else {
        await postData(config.addEndpoint, { movie_id: movieId });
      }
    },
    onMutate: async () => {
      console.log("🚀 OPTIMISTIC UPDATE START:", {
        logName: config.logName,
        movieId,
        configCurrentValue: config.currentValue,
      });

      // Cancel outgoing refetches using centralized cache key
      const movieDetailKey = CacheKeys.movies.detail(movieId);
      await queryClient.cancelQueries({ queryKey: movieDetailKey });

      // Snapshot previous value
      const previousData =
        queryClient.getQueryData<MovieDetailData>(movieDetailKey);

      console.log("📷 CACHE SNAPSHOT:", {
        movieDetailKey,
        hasPreviousData: !!previousData,
        previousUserInteractions: previousData?.user_interactions,
      });

      // Optimistically update movie detail cache
      updateCache((oldData: MovieDetailData | MovieDetailResponse) => {
        const newState = !config.currentValue; // Use config.currentValue, not cache value

        // Handle ResponseBuilder format (NEW - this is what the BFF API returns now)
        if ("data" in oldData && "context" in oldData) {
          const responseData = oldData as MovieDetailResponse;
          const cacheCurrentValue =
            responseData.context.user_interactions?.[config.cacheKey] ?? false;

          console.log("💾 CACHE UPDATE (ResponseBuilder):", {
            logName: config.logName,
            cacheKey: config.cacheKey,
            oldCacheValue: cacheCurrentValue,
            configCurrentValue: config.currentValue,
            newState,
            oldUserInteractions: responseData.context.user_interactions,
            similarMoviesCount:
              responseData.related?.similar_movies?.length || 0,
          });

          // Update similar movies if the current movie appears in the similar movies list
          const updatedSimilarMovies =
            responseData.related?.similar_movies?.map(
              (similarMovie: SimilarMovie) => {
                if (similarMovie.id === movieId) {
                  const movieProperty =
                    config.cacheKey === "is_watched"
                      ? "watched"
                      : config.cacheKey === "is_favorite"
                      ? "liked"
                      : "in_watchlist";

                  console.log("🎬 UPDATING SIMILAR MOVIE:", {
                    movieId: similarMovie.id,
                    property: movieProperty,
                    oldValue: similarMovie[movieProperty],
                    newValue: newState,
                  });

                  return {
                    ...similarMovie,
                    [movieProperty]: newState,
                  } as SimilarMovie;
                }
                return similarMovie;
              }
            ) ||
            responseData.related?.similar_movies ||
            [];

          const updatedData: MovieDetailResponse = {
            ...responseData,
            context: {
              ...responseData.context,
              user_interactions: {
                ...(responseData.context.user_interactions || {}),
                [config.cacheKey]: newState,
              },
            },
            related: {
              ...responseData.related,
              similar_movies: updatedSimilarMovies,
            },
          };

          console.log("💾 UPDATED CACHE DATA (ResponseBuilder):", {
            newUserInteractions: updatedData.context.user_interactions,
            updatedSimilarMoviesCount: updatedSimilarMovies.length,
          });

          return updatedData;
        }

        // Handle legacy format (OLD - fallback for any remaining legacy cache)
        else if ("user_interactions" in oldData) {
          const legacyData = oldData as MovieDetailData;
          const cacheCurrentValue =
            legacyData.user_interactions?.[config.cacheKey] ?? false;

          console.log("💾 CACHE UPDATE (Legacy):", {
            logName: config.logName,
            cacheKey: config.cacheKey,
            oldCacheValue: cacheCurrentValue,
            configCurrentValue: config.currentValue,
            newState,
            oldUserInteractions: legacyData.user_interactions,
          });

          const updatedData: MovieDetailData = {
            ...legacyData,
            user_interactions: {
              ...(legacyData.user_interactions || {}),
              [config.cacheKey]: newState,
            },
          };

          console.log("💾 UPDATED CACHE DATA (Legacy):", {
            newUserInteractions: updatedData.user_interactions,
          });

          return updatedData;
        }

        // Unknown format - log and return unchanged
        console.log("💾 UNKNOWN CACHE FORMAT - NOT UPDATING:", {
          dataKeys: Object.keys(oldData),
          hasData: "data" in oldData,
          hasContext: "context" in oldData,
          hasUserInteractions: "user_interactions" in oldData,
          oldData: oldData,
        });
        return oldData;
      });

      // Optimistically update movie lists cache
      updateMovieListsCache((movie) => {
        const newState = !config.currentValue;

        console.log("📋 LIST UPDATE:", {
          logName: config.logName,
          movieId: movie.id,
          currentMovieProperty:
            movie[
              config.cacheKey === "is_watched"
                ? "watched"
                : config.cacheKey === "is_favorite"
                ? "liked"
                : config.cacheKey === "in_watchlist"
                ? "in_watchlist"
                : config.cacheKey
            ],
          newState,
        });

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

      // Also update any other movie detail caches that might contain this movie as a similar movie
      console.log("🔄 CHECKING FOR OTHER MOVIE CACHES TO UPDATE");
      const allQueries = queryClient.getQueryCache().getAll();
      const otherMovieDetailQueries = allQueries.filter(
        (query) =>
          query.queryKey[0] === "movies" &&
          query.queryKey[1] === "detail" &&
          query.queryKey[2] !== movieId &&
          query.state.data
      );

      otherMovieDetailQueries.forEach((query) => {
        const cacheData = query.state.data as MovieDetailResponse;
        if (cacheData?.related?.similar_movies) {
          const hasSimilarMovie = cacheData.related.similar_movies.some(
            (sim: SimilarMovie) => sim.id === movieId
          );
          if (hasSimilarMovie) {
            console.log("🔄 UPDATING SIMILAR MOVIE IN OTHER CACHE:", {
              otherMovieId: query.queryKey[2],
              currentMovieId: movieId,
            });

            queryClient.setQueryData(query.queryKey, (oldData: unknown) => {
              const typedOldData = oldData as MovieDetailResponse;
              if (!typedOldData?.related?.similar_movies) return oldData;

              return {
                ...typedOldData,
                related: {
                  ...typedOldData.related,
                  similar_movies: typedOldData.related.similar_movies.map(
                    (sim: SimilarMovie) => {
                      if (sim.id === movieId) {
                        const movieProperty =
                          config.cacheKey === "is_watched"
                            ? "watched"
                            : config.cacheKey === "is_favorite"
                            ? "liked"
                            : "in_watchlist";
                        return {
                          ...sim,
                          [movieProperty]: !config.currentValue,
                        } as SimilarMovie;
                      }
                      return sim;
                    }
                  ),
                },
              } as MovieDetailResponse;
            });
          }
        }
      });

      console.log("✅ OPTIMISTIC UPDATE COMPLETE");
      return { previousData };
    },
    onError: (
      err: Error,
      _variables: unknown,
      context: { previousData?: MovieDetailData } | undefined
    ) => {
      console.log("❌ MUTATION ERROR:", {
        error: err.message,
        logName: config.logName,
        movieId,
        hasContext: !!context,
        hasPreviousData: !!context?.previousData,
      });

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
        console.log("🔄 ROLLBACK COMPLETE");
      }

      // Invalidate caches on error to ensure fresh data
      invalidateRelatedCaches();
    },
    onSuccess: () => {
      console.log("✅ MUTATION SUCCESS:", {
        logName: config.logName,
        movieId,
      });

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
      console.log("🏁 MUTATION SETTLED:", {
        logName: config.logName,
        movieId,
      });

      // Force a cache invalidation to ensure consistency
      // This might be needed if optimistic updates aren't working properly
      const movieDetailKey = CacheKeys.movies.detail(movieId);
      queryClient.invalidateQueries({ queryKey: movieDetailKey });

      console.log("🔄 FORCED CACHE INVALIDATION");
    },
  });

  // Create the three mutations using useMutation at the top level
  const toggleWatched = useMutation(
    createMutationConfig({
      addEndpoint: `/bff/v1/me/watched-movies`,
      removeEndpoint: `/bff/v1/me/watched-movies/${movieId}`,
      currentValue: movie?.watched ?? false,
      cacheKey: "is_watched",
      logName: "watched",
    })
  );

  const toggleLiked = useMutation(
    createMutationConfig({
      addEndpoint: `/bff/v1/me/liked-movies`,
      removeEndpoint: `/bff/v1/me/liked-movies/${movieId}`,
      currentValue: movie?.liked ?? false,
      cacheKey: "is_favorite",
      logName: "liked",
    })
  );

  const toggleWatchlist = useMutation(
    createMutationConfig({
      addEndpoint: `/bff/v1/me/watchlist`,
      removeEndpoint: `/bff/v1/me/watchlist/movies/${movieId}`,
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
