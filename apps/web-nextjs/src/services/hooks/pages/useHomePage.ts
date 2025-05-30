"use client";

import { Movie } from "@/domain/entities";
import { MovieAPI, MovieListResponse } from "@/services/api";
import { CacheKeys } from "@/services/cache";
import useMovieFilterStore from "@/store/movieFilterStore";
import { useInfiniteQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo } from "react";
import { createLogger } from "@/utils/logging";

// Create logger for this hook
const logger = createLogger("useHomePage");

interface UseHomePageOptions {
  movie_id?: number;
  actor_id?: number;
  genre_id?: number;
  searchQuery?: string;
  initialPage?: number;
  limit?: number;
}

/**
 * Hook for fetching and managing home page movies with filter integration
 *
 * Enhanced with simplified cache integration:
 * - Uses centralized cache keys for consistency
 * - Smart filter-based invalidation
 * - Automatic prefetching of movie details
 */
export const useHomePage = (options: UseHomePageOptions) => {
  const queryClient = useQueryClient();

  // Get filters from the centralized store
  const { filters } = useMovieFilterStore();

  // Extract filter values
  const {
    imdb_rating,
    rotten_tomatoes_rating,
    metacritic_rating,
    year,
    sortOrder = "release_date",
    sortDesc = true,
  } = filters;

  logger.debug("useHomePage initialized", {
    filters: {
      imdb_rating,
      rotten_tomatoes_rating,
      metacritic_rating,
      year,
      sortOrder,
      sortDesc,
    },
  });

  // Use centralized cache keys - much simpler approach
  const queryKey = useMemo(() => {
    const baseKey = options.genre_id
      ? CacheKeys.movies.genreList(options.genre_id.toString(), "filtered")
      : options.actor_id
      ? CacheKeys.movies.actorList(options.actor_id.toString(), "filtered")
      : CacheKeys.movies.home();

    // Add filter parameters as additional cache key segment
    return [
      ...baseKey,
      {
        imdb_rating,
        rotten_tomatoes_rating,
        metacritic_rating,
        year,
        sortOrder,
        sortDesc,
      },
    ] as const;
  }, [
    options.genre_id,
    options.actor_id,
    imdb_rating,
    rotten_tomatoes_rating,
    metacritic_rating,
    year,
    sortOrder,
    sortDesc,
  ]);

  // Smart invalidation when filters change - improved granular approach
  useEffect(() => {
    logger.info(
      "Filter changes detected, using granular invalidation strategy",
      {
        sortOrder,
        sortDesc,
        year,
        imdb_rating,
      }
    );

    // Only invalidate queries that are actually affected by these specific filters
    queryClient.invalidateQueries({
      predicate: (query) => {
        if (query.queryKey[0] !== "movies" || query.queryKey[1] !== "lists") {
          return false;
        }

        // Check if this query uses the same filter parameters
        const queryKey = query.queryKey as unknown[];
        const filterSegment = queryKey[queryKey.length - 1];

        if (typeof filterSegment === "object" && filterSegment !== null) {
          // Only invalidate if this query has matching base parameters
          // (same genre_id, actor_id, or home context)
          const baseMatches =
            (options.genre_id &&
              queryKey[2] === "genre" &&
              queryKey[3] === options.genre_id.toString()) ||
            (options.actor_id &&
              queryKey[2] === "actor" &&
              queryKey[3] === options.actor_id.toString()) ||
            (!options.genre_id && !options.actor_id && queryKey[2] === "home");

          return baseMatches;
        }

        return false;
      },
    });
  }, [
    sortOrder,
    sortDesc,
    year,
    imdb_rating,
    rotten_tomatoes_rating,
    metacritic_rating,
    queryClient,
    options.genre_id,
    options.actor_id,
  ]);

  const {
    data,
    isLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    error,
    refetch,
  } = useInfiniteQuery({
    queryKey,
    queryFn: async ({ pageParam = options.initialPage || 1 }) => {
      logger.debug(`Fetching page ${pageParam} for home page`);

      logger.info("Fetching movies with BFF API", {
        page: pageParam,
        limit: options.limit || 20,
        filters: {
          genre_id: options.genre_id,
          actor_id: options.actor_id,
          sort_by: sortOrder,
          sort_desc: sortDesc,
          year,
          imdb_rating,
          rotten_tomatoes_rating,
          metacritic_rating,
        },
      });

      const response = await MovieAPI.getMovies({
        page: pageParam,
        limit: options.limit || 20,
        genre_id: options.genre_id,
        actor_id: options.actor_id,
        sort_by: sortOrder,
        sort_desc: sortDesc,
        year,
        imdb_rating,
        rotten_tomatoes_rating,
        metacritic_rating,
      });

      // Simple prefetching - use the existing MovieAPI.getById method
      if (pageParam === 1 && response.results.length > 0) {
        const firstFewMovies = response.results.slice(0, 3);
        firstFewMovies.forEach((movie) => {
          if (movie.id) {
            // Check if movie details are already cached
            const movieDetailsKey = CacheKeys.movies.detail(movie.id as number);
            if (!queryClient.getQueryData(movieDetailsKey)) {
              // Prefetch movie details in background
              queryClient.prefetchQuery({
                queryKey: movieDetailsKey,
                queryFn: () => MovieAPI.getById(movie.id as number),
                staleTime: 1000 * 60 * 5, // 5 minutes
              });
            }
          }
        });
      }

      return response;
    },
    getNextPageParam: (lastPage: MovieListResponse) => {
      return lastPage.has_next ? lastPage.page + 1 : undefined;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
  });

  // Calculate total fetched movies count
  const fetchedMoviesCount =
    data?.pages?.reduce((total, page) => total + page.results.length, 0) || 0;

  // Flatten all movies from all pages
  const movies: Movie[] = useMemo(() => {
    return data?.pages ? data.pages.flatMap((page) => page.results) : [];
  }, [data?.pages]);

  // Get pagination info from the last page
  const lastPage = data?.pages?.[data.pages.length - 1];
  const totalMovies = lastPage?.total || 0;
  const currentPage = lastPage?.page || 1;

  // Log results or errors
  useEffect(() => {
    if (error) {
      logger.error("Error fetching movies via BFF:", error);
    } else if (fetchedMoviesCount > 0) {
      logger.info(
        `Fetched ${fetchedMoviesCount} movies from ${
          data?.pages?.length || 0
        } pages (total: ${totalMovies})`
      );

      // Log a sample movie to verify user interaction data
      const firstMovie = data?.pages?.[0]?.results?.[0];
      if (firstMovie) {
        logger.debug("Sample movie with user interactions:", {
          id: firstMovie.id,
          title: firstMovie.title,
          watched: firstMovie.watched,
          liked: firstMovie.liked,
          in_watchlist: firstMovie.in_watchlist,
        });
      }
    }
  }, [error, fetchedMoviesCount, totalMovies, data?.pages]);

  // Simple cache utilities - only what's actually useful
  const cache = useMemo(
    () => ({
      /**
       * Get the current cache key being used
       */
      getCacheKey: () => queryKey,

      /**
       * Invalidate all movie list queries (useful for global refresh)
       */
      invalidateMovieLists: () => {
        return queryClient.invalidateQueries({
          predicate: (query) => {
            return (
              query.queryKey[0] === "movies" && query.queryKey[1] === "lists"
            );
          },
        });
      },

      /**
       * Prefetch movie details for performance
       */
      prefetchMovieDetails: (movieId: number) => {
        const movieDetailsKey = CacheKeys.movies.detail(movieId);
        if (!queryClient.getQueryData(movieDetailsKey)) {
          return queryClient.prefetchQuery({
            queryKey: movieDetailsKey,
            queryFn: () => MovieAPI.getById(movieId),
            staleTime: 1000 * 60 * 5,
          });
        }
      },
    }),
    [queryKey, queryClient]
  );

  return {
    // Data
    movies,
    totalMovies,
    fetchedMoviesCount,
    currentPage,

    // Loading states
    isLoading,
    isFetchingNextPage,

    // Pagination
    hasNextPage,
    fetchNextPage,

    // Error handling
    error,
    refetch,

    // Simple, useful cache utilities
    cache,

    // Raw data for advanced use cases
    rawData: data,
  };
};
