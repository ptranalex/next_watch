"use client";

import { fetchData } from "@/services/api";
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
const logger = createLogger("useTopMoviesByYear");

// Response type for top movies (same as MovieListData)
interface TopMoviesResponse {
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  results: Movie[];
}

interface UseTopMoviesByYearOptions {
  yearParam: string; // The year parameter from the URL (could be "current-year", "all-time", or a specific year)
}

/**
 * Hook for fetching and managing top-rated movies by year
 * Handles special cases:
 * - "current-year": Uses current year and locks it in filter
 * - "all-time": Shows all years, no year filter
 * - Specific year: Filters by that year and locks it
 *
 * @param options - Configuration including yearParam from URL
 * @returns Top movies data, loading state, error, and movies using standard Movie format with pagination support and filtering
 */
export function useTopMoviesByYear({ yearParam }: UseTopMoviesByYearOptions) {
  const queryClient = useQueryClient();

  // Log hook initialization
  logger.debug("useTopMoviesByYear initialized", { yearParam });

  // Get filters from the store
  const { filters, setFilter, lockFilters, unlockAllFilters } =
    useMovieFilterStore();

  const currentYear = new Date().getFullYear();

  // Set up filters based on yearParam when it changes
  useEffect(() => {
    if (yearParam === "current-year") {
      logger.info(`Setting top movies for current year: ${currentYear}`);
      unlockAllFilters();
      setFilter("year", currentYear);
      setFilter("sortOrder", "imdb_rating");
      setFilter("sortDesc", true);
      lockFilters(["year", "sortOrder"]);
    } else if (yearParam === "all-time") {
      logger.info("Setting top movies of all time");
      unlockAllFilters();
      setFilter("year", undefined); // Clear year filter for all-time
      setFilter("sortOrder", "imdb_rating");
      setFilter("sortDesc", true);
      lockFilters(["sortOrder"]); // Only lock sort order, not year
    } else {
      // Normal numeric year handling
      const year = parseInt(yearParam, 10);
      if (!isNaN(year)) {
        logger.info(`Setting top movies for year: ${year}`);
        unlockAllFilters();
        setFilter("year", year);
        setFilter("sortOrder", "imdb_rating");
        setFilter("sortDesc", true);
        lockFilters(["year", "sortOrder"]);
      }
    }

    // Cleanup function: unlock filters when yearParam changes or component unmounts
    return () => {
      logger.debug("🔓 Cleaning up: unlocking filters");
      unlockAllFilters();
    };
  }, [yearParam, currentYear, setFilter, lockFilters, unlockAllFilters]);

  // Extract filter values for cleaner logging and cache keys
  const {
    imdb_rating,
    rotten_tomatoes_rating,
    metacritic_rating,
    year,
    sortOrder = "imdb_rating",
    sortDesc = true,
  } = filters;

  // Use centralized cache keys for consistency
  const queryKey = useMemo(() => {
    const baseKey = CacheKeys.movies.topByYear(yearParam);

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
    yearParam,
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
      yearParam,
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
    yearParam,
  ]);

  // Build query parameters from filters
  const queryParams = useMemo(() => {
    const params: Record<string, string | number | boolean> = {};

    // Year handling based on yearParam
    if (yearParam === "current-year") {
      params.year = currentYear;
    } else if (yearParam === "all-time") {
      // No year filter for all-time
    } else {
      const year = parseInt(yearParam, 10);
      if (!isNaN(year)) {
        params.year = year;
      }
    }

    if (filters.imdb_rating !== undefined) {
      params.imdb_rating = filters.imdb_rating;
    }

    if (filters.rotten_tomatoes_rating !== undefined) {
      params.rotten_tomatoes_rating = filters.rotten_tomatoes_rating;
    }
    if (filters.metacritic_rating !== undefined) {
      params.metacritic_rating = filters.metacritic_rating;
    }

    // Default sorting by IMDb rating (highest first) for top movies
    params.sort_by = filters.sortOrder || "imdb_rating";
    params.sort_desc = filters.sortDesc !== undefined ? filters.sortDesc : true;

    return params;
  }, [filters, yearParam, currentYear]);

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

  // Fetch top movies with pagination support and filtering
  const {
    data: moviesData,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
    error,
    refetch,
  } = useInfiniteQuery({
    queryKey,
    queryFn: async ({ pageParam = 1 }) => {
      const baseUrl = `/bff/v1/top?page=${pageParam}&limit=20`;
      const urlWithFilters = queryString
        ? `${baseUrl}&${queryString}`
        : baseUrl;

      logger.info(
        `Fetching top movies page ${pageParam} for year "${yearParam}" with filters: ${queryString}`
      );

      const response = await fetchData<TopMoviesResponse>(urlWithFilters);

      return response;
    },
    getNextPageParam: (lastPage) => {
      return lastPage.has_next ? (lastPage.page || 1) + 1 : undefined;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
    onSuccess: (data: InfiniteData<TopMoviesResponse>) => {
      // Log successful data loading
      const firstPage = data?.pages?.[0];
      if (firstPage) {
        logger.info("Loaded top movies successfully", {
          year: yearParam,
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
          logger.debug("Sample top movie with user interactions:", {
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
        logger.info(`Top movies for year "${yearParam}" not found (404)`, {
          year: yearParam,
        });
      } else {
        logger.error(
          `Error loading top movies for year "${yearParam}":`,
          error
        );
      }
    },
  });

  // Flatten all movies from all pages
  const allMovies = useMemo(() => {
    if (!moviesData?.pages) return [];

    const movies = moviesData.pages.flatMap(
      (page) => page.results || []
    ) as Movie[];

    logger.debug(
      `Total top movies loaded: ${movies.length} for year "${yearParam}" (with filters: ${queryString})`
    );
    return movies;
  }, [moviesData?.pages, yearParam, queryString]);

  // Get pagination metadata from the latest page
  const latestPage = moviesData?.pages?.[moviesData.pages.length - 1];
  const totalMovies = latestPage?.total || 0;
  const currentPage = latestPage?.page || 1;
  const totalPages = latestPage?.total_pages || 0;
  const hasPrevPage = latestPage?.has_prev || false;

  // Load more function
  const loadMore = () => {
    if (hasNextPage && !isFetchingNextPage) {
      logger.info(
        `Loading more top movies for year "${yearParam}", page ${
          currentPage + 1
        } (with filters: ${queryString})`
      );
      fetchNextPage();
    }
  };

  // Log errors
  useEffect(() => {
    if (error) {
      logger.error(`Error fetching top movies for year "${yearParam}":`, error);
    }
  }, [error, yearParam]);

  // Calculate title text based on yearParam
  const titleText = useMemo(() => {
    if (yearParam === "current-year") {
      return `Top Movies of ${currentYear} (Current Year)`;
    } else if (yearParam === "all-time") {
      return "Top Movies of All Time";
    } else {
      const year = parseInt(yearParam, 10);
      return `Top Movies from ${!isNaN(year) ? year : currentYear}`;
    }
  }, [yearParam, currentYear]);

  // Calculate total fetched movies count
  const fetchedMoviesCount = allMovies.length;

  // Log results
  useEffect(() => {
    if (error) {
      logger.error("Error fetching top movies:", error);
    } else if (fetchedMoviesCount > 0) {
      logger.info(
        `Fetched ${fetchedMoviesCount} top movies from ${
          moviesData?.pages?.length || 0
        } pages for year "${yearParam}" (total: ${totalMovies})`
      );

      // Log a sample movie to verify user interaction data
      const firstMovie = moviesData?.pages?.[0]?.results?.[0];
      if (firstMovie) {
        logger.debug("Sample top movie with user interactions:", {
          id: firstMovie.id,
          title: firstMovie.title,
          watched: firstMovie.watched,
          liked: firstMovie.liked,
          in_watchlist: firstMovie.in_watchlist,
        });
      }
    }
  }, [error, fetchedMoviesCount, totalMovies, moviesData?.pages, yearParam]);

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

    // Title for the page
    titleText,

    // Top movies specific metadata
    defaultFilters: {
      imdb_rating: 7.0,
      sort_by: "imdb_rating",
      sort_desc: true,
    },

    // Cache utilities (consistent with other hooks)
    cache,

    // Raw data for advanced use cases
    rawData: moviesData,
  };
}
