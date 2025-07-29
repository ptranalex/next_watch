"use client";

import { Movie } from "@/domain/entities";
import { MoviesAPI } from "@/services/api";
import { BFFMovieListResponseRB } from "@/services/api/bff/types";
import { CacheKeys } from "@/services/cache";
import useMovieFilterStore from "@/store/movieFilterStore";
import {
  useInfiniteQuery,
  useQueryClient,
  InfiniteData,
} from "@tanstack/react-query";
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

      const response = await MoviesAPI.getMovies({
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

      return response;
    },
    getNextPageParam: (lastPage: BFFMovieListResponseRB) => {
      // New ResponseBuilder format only
      return lastPage.pagination.has_next
        ? (lastPage.pagination.page || 0) + 1
        : undefined;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
    onSuccess: (data: InfiniteData<BFFMovieListResponseRB>) => {
      // Log successful data loading
      const firstPage = data?.pages?.[0];
      if (firstPage) {
        const totalMovies = firstPage.pagination?.total || 0;
        const moviesOnFirstPage = firstPage.results?.length || 0;
        const currentPage = firstPage.pagination?.page || 1;
        const totalPages = firstPage.pagination?.total_pages || 0;

        logger.info("Loaded home page movies successfully", {
          totalMovies,
          currentPage,
          totalPages,
          moviesOnFirstPage,
          hasFilters: !!(
            options.genre_id ||
            options.actor_id ||
            year ||
            imdb_rating ||
            rotten_tomatoes_rating ||
            metacritic_rating
          ),
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

        // Log a sample movie to verify data structure
        const firstMovie = firstPage.results?.[0];
        if (firstMovie) {
          logger.debug("Sample home page movie with user interactions:", {
            id: firstMovie.id,
            title: firstMovie.title,
            watched: firstMovie.watched,
            liked: firstMovie.liked,
            in_watchlist: firstMovie.in_watchlist,
          });
        }
      }
    },
    onError: (error: unknown) => {
      // Handle specific error types for better UX
      const apiError = error as { status?: number };
      if (apiError.status === 404) {
        logger.info("Home page movies not found (404)");
      } else {
        logger.error("Error loading home page movies:", error);
      }
    },
  });

  // Calculate total fetched movies count
  const fetchedMoviesCount =
    data?.pages?.reduce((total, page) => total + page.results.length, 0) || 0;

  // Flatten all movies from all pages
  const movies: Movie[] = useMemo(() => {
    return data?.pages ? data.pages.flatMap((page) => page.results) : [];
  }, [data?.pages]);

  // Get pagination info from the last page (ResponseBuilder format)
  const lastPage = data?.pages?.[data.pages.length - 1];
  const totalMovies = lastPage?.pagination?.total || 0;
  const currentPage = lastPage?.pagination?.page || 1;

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
            queryFn: () => MoviesAPI.getMovieDetail(movieId),
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
