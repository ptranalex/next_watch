"use client";

import { fetchData } from "@/services/api";
import { useInfiniteQuery, useQueryClient } from "@tanstack/react-query";
import { createLogger } from "@/utils/logging";
import { useEffect, useMemo } from "react";
import { Movie } from "@/domain/entities";
import useMovieFilterStore from "@/store/movieFilterStore";
import { CacheKeys } from "@/services/cache";
import { MovieAPI } from "@/services/api";

// Create logger for this hook
const logger = createLogger("useWatchedPage");

// Type for watched movies response
interface WatchedMoviesResponse {
  results: Movie[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  metadata?: {
    [key: string]: unknown;
  };
}

/**
 * Hook for managing watched movies page data with filtering and pagination
 * Enhanced with cache integration:
 * - Uses centralized cache keys for consistency
 * - Smart filter-based invalidation
 * - Automatic prefetching of movie details
 * - Local cache utilities for performance
 */
export function useWatchedPage() {
  const queryClient = useQueryClient();

  // Log hook initialization
  logger.debug(`useWatchedPage initialized`);

  // Get filters from the store
  const { filters } = useMovieFilterStore();

  // Extract filter values for cleaner logging and cache keys
  const {
    imdb_rating,
    rotten_tomatoes_rating,
    metacritic_rating,
    year,
    sortOrder = "release_date",
    sortDesc = true,
  } = filters;

  logger.debug("useWatchedPage initialized", {
    filters: {
      imdb_rating,
      rotten_tomatoes_rating,
      metacritic_rating,
      year,
      sortOrder,
      sortDesc,
    },
  });

  // Use centralized cache keys for consistency
  const queryKey = useMemo(() => {
    const baseKey = CacheKeys.movies.user.watched();

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
    imdb_rating,
    rotten_tomatoes_rating,
    metacritic_rating,
    year,
    sortOrder,
    sortDesc,
  ]);

  // Smart invalidation when filters change
  useEffect(() => {
    logger.info("Filter changes detected, invalidating movie list queries", {
      sortOrder,
      sortDesc,
      year,
      imdb_rating,
    });

    // Invalidate all movie list queries when filters change
    queryClient.invalidateQueries({
      predicate: (query) => {
        return query.queryKey[0] === "movies" && query.queryKey[1] === "lists";
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
  ]);

  // Build query parameters from filters for API call
  const queryParams = useMemo(() => {
    const params: Record<string, string | number | boolean> = {};

    if (imdb_rating !== undefined) {
      params.imdb_rating = imdb_rating;
    }
    if (rotten_tomatoes_rating !== undefined) {
      params.rotten_tomatoes_rating = rotten_tomatoes_rating;
    }
    if (metacritic_rating !== undefined) {
      params.metacritic_rating = metacritic_rating;
    }
    if (year !== undefined) {
      params.year = year;
    }
    if (sortOrder) {
      params.sort_by = sortOrder;
    }
    if (sortDesc !== undefined) {
      params.sort_desc = sortDesc;
    }

    return params;
  }, [
    imdb_rating,
    metacritic_rating,
    rotten_tomatoes_rating,
    sortDesc,
    sortOrder,
    year,
  ]);

  // Convert params to URL search string
  const queryString = useMemo(() => {
    const searchParams = new URLSearchParams();
    Object.entries(queryParams).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    });
    return searchParams.toString();
  }, [queryParams]);

  // Fetch watched movies with pagination support and filtering
  const {
    data: watchedData,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
    error,
    refetch,
  } = useInfiniteQuery({
    queryKey,
    queryFn: async ({ pageParam = 1 }) => {
      const baseUrl = `/bff/v1/watched?page=${pageParam}&limit=20`;
      const urlWithFilters = queryString
        ? `${baseUrl}&${queryString}`
        : baseUrl;

      logger.info(
        `Fetching watched movies page ${pageParam} with filters: ${queryString}`
      );

      const response = await fetchData<WatchedMoviesResponse>(urlWithFilters);

      // Simple prefetching - prefetch details for first 3 movies on first page
      if (pageParam === 1 && response.results && response.results.length > 0) {
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
    getNextPageParam: (lastPage) => {
      return lastPage.pagination.has_next
        ? (lastPage.pagination.page || 1) + 1
        : undefined;
    },
    enabled: true,
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
  });

  // Flatten all movies from all pages
  const allMovies = useMemo(() => {
    if (!watchedData?.pages) return [];

    const movies = watchedData.pages.flatMap(
      (page) => page.results || []
    ) as Movie[];

    logger.debug(
      `Total watched movies loaded: ${movies.length} (with filters: ${queryString})`
    );
    return movies;
  }, [watchedData?.pages, queryString]);

  // Calculate total fetched movies count
  const fetchedMoviesCount = allMovies.length;

  // Get pagination metadata from the latest page
  const latestPage = watchedData?.pages?.[watchedData.pages.length - 1];
  const totalMovies = latestPage?.pagination.total || 0;
  const currentPage = latestPage?.pagination.page || 1;
  const totalPages = latestPage?.pagination.total_pages || 0;
  const hasPrevPage = latestPage?.pagination.has_prev || false;

  // Load more function
  const loadMore = () => {
    if (hasNextPage && !isFetchingNextPage) {
      logger.info(
        `Loading more watched movies, page ${
          currentPage + 1
        } (with filters: ${queryString})`
      );
      fetchNextPage();
    }
  };

  // Log errors
  useEffect(() => {
    if (error) {
      logger.error(`Error fetching watched movies:`, error);
    }
  }, [error]);

  // Log filter changes
  useEffect(() => {
    logger.info(`Watched movies filters updated:`, queryParams);
  }, [queryParams]);

  // Log results
  useEffect(() => {
    if (error) {
      logger.error("Error fetching watched movies:", error);
    } else if (fetchedMoviesCount > 0) {
      logger.info(
        `Fetched ${fetchedMoviesCount} watched movies from ${
          watchedData?.pages?.length || 0
        } pages (total: ${totalMovies})`
      );

      // Log a sample movie to verify user interaction data
      const firstMovie = watchedData?.pages?.[0]?.results?.[0];
      if (firstMovie) {
        logger.debug("Sample watched movie with user interactions:", {
          id: firstMovie.id,
          title: firstMovie.title,
          watched: firstMovie.watched,
          liked: firstMovie.liked,
          in_watchlist: firstMovie.in_watchlist,
        });
      }
    }
  }, [error, fetchedMoviesCount, totalMovies, watchedData?.pages]);

  // Cache utilities - consistent with other hooks
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
    // Movie data
    movies: allMovies,
    totalMovies,
    fetchedMoviesCount,
    currentPage,
    totalPages,

    // Loading states
    isLoading,
    isFetchingNextPage,

    // Pagination
    hasNextPage: !!hasNextPage,
    hasPrevPage,
    loadMore,
    fetchNextPage,

    // Error handling
    error,
    refetch,

    // Filter-related data
    activeFilters: queryParams,
    hasActiveFilters: Object.keys(queryParams).length > 0,

    // Cache utilities (consistent with other hooks)
    cache,

    // Raw data for advanced use cases
    rawData: watchedData,
  };
}
