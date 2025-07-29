"use client";

import { fetchData, GenreScreenData } from "@/services/api";
import {
  useInfiniteQuery,
  useQueryClient,
  InfiniteData,
} from "@tanstack/react-query";
import { createLogger } from "@/utils/logging";
import { useEffect, useMemo } from "react";
import { Movie } from "@/domain/entities";
import useMovieFilterStore from "@/store/movieFilterStore";
import { CacheKeys } from "@/services/cache";
import { MovieAPI } from "@/services/api";

// Create logger for this hook
const logger = createLogger("useGenrePage");

/**
 * Hook for fetching and managing a single genre with its movies
 * Enhanced with cache integration:
 * - Uses centralized cache keys for consistency
 * - Smart filter-based invalidation
 * - Automatic prefetching of movie details
 * - Local cache utilities for performance
 *
 * @param id - Genre ID to fetch
 * @returns Genre data, loading state, error, movies, and cache utilities
 */
export function useGenrePage(id: number) {
  const queryClient = useQueryClient();

  // Log hook initialization
  logger.debug(`useGenrePage initialized with id: ${id}`);

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

  logger.debug("useGenrePage initialized", {
    genreId: id,
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
    const baseKey = CacheKeys.movies.genreList(id.toString(), "filtered");

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
    id,
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
      genreId: id,
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
    id,
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

  // Fetch genre and movies with pagination support and filtering
  const {
    data: genreData,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
    error,
    refetch,
  } = useInfiniteQuery({
    queryKey,
    queryFn: async ({ pageParam = 1 }) => {
      const baseUrl = `/bff/v1/genres/${id}?page=${pageParam}&limit=20`;
      const urlWithFilters = queryString
        ? `${baseUrl}&${queryString}`
        : baseUrl;

      logger.info(
        `Fetching genre screen data page ${pageParam} for id: ${id} with filters: ${queryString}`
      );

      const response = await fetchData<GenreScreenData>(urlWithFilters);

      return response;
    },
    getNextPageParam: (lastPage) => {
      return lastPage.has_next ? (lastPage.page || 1) + 1 : undefined;
    },
    enabled: !!id,
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
    onSuccess: (data: InfiniteData<GenreScreenData>) => {
      // Log successful data loading
      const firstPage = data?.pages?.[0];
      if (firstPage) {
        logger.info("Loaded genre data successfully", {
          genreId: id,
          genreName: firstPage.genre?.name,
          totalMovies: firstPage.total || 0,
          currentPage: firstPage.page || 1,
          totalPages: firstPage.total_pages || 0,
          moviesOnFirstPage: firstPage.results?.length || 0,
          hasFilters: Object.keys(queryParams).length > 0,
          filters: queryParams,
        });

        // Log a sample movie to verify data structure
        const firstMovie = firstPage.results?.[0];
        if (firstMovie) {
          logger.debug("Sample genre movie with user interactions:", {
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
        logger.info(`Genre ${id} not found (404)`, { genreId: id });
      } else {
        logger.error(`Error loading genre ${id} data:`, error);
      }
    },
  });

  // Extract genre info from first page
  const genre = genreData?.pages?.[0]?.genre;
  const genreName = genre?.name || "Genre";

  // Flatten all movies from all pages
  const allMovies = useMemo(() => {
    if (!genreData?.pages) return [];

    const movies = genreData.pages.flatMap(
      (page) => page.results || []
    ) as Movie[];

    logger.debug(
      `Total movies loaded: ${movies.length} (with filters: ${queryString})`
    );
    return movies;
  }, [genreData?.pages, queryString]);

  // Calculate total fetched movies count
  const fetchedMoviesCount = allMovies.length;

  // Get pagination metadata from the latest page
  const latestPage = genreData?.pages?.[genreData.pages.length - 1];
  const totalMovies = latestPage?.total || 0;
  const currentPage = latestPage?.page || 1;
  const totalPages = latestPage?.total_pages || 0;
  const hasPrevPage = latestPage?.has_prev || false;

  // Load more function
  const loadMore = () => {
    if (hasNextPage && !isFetchingNextPage) {
      logger.info(
        `Loading more movies for genre ${id}, page ${
          currentPage + 1
        } (with filters: ${queryString})`
      );
      fetchNextPage();
    }
  };

  // Log filter changes
  useEffect(() => {
    logger.info(`Genre ${id} filters updated:`, queryParams);
  }, [id, queryParams]);

  // Cache utilities - consistent with useHomePage
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
    // Genre data
    genre,
    genreName,

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

    // Error handling - exposed for component-level handling (consistent with useMovieDetailPage)
    error,
    refetch,

    // Filter-related data
    activeFilters: queryParams,
    hasActiveFilters: Object.keys(queryParams).length > 0,

    // Cache utilities (consistent with useHomePage)
    cache,

    // Raw data for advanced use cases
    rawData: genreData,
  };
}
