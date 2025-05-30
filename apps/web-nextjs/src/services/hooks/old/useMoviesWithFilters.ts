"use client";

import { Movie } from "@/domain/entities";
import { MovieAPI, MovieListResponse } from "@/services/api";
import useMovieFilterStore from "@/store/movieFilterStore";
import { useInfiniteQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { createLogger } from "@/utils/logging";

// Create logger for this hook
const logger = createLogger("useMoviesWithFilters");

/**
 * Ensures all movie objects have default values for user interaction properties
 *
 * @param movies - Array of movies to process
 * @returns Array of movies with default values for user interaction properties
 */
const ensureUserInteractions = (movies: Movie[]): Movie[] => {
  return movies.map((movie) => ({
    ...movie,
    watched: movie.watched ?? false,
    liked: movie.liked ?? false,
    in_watchlist: movie.in_watchlist ?? false,
  }));
};

interface UseMoviesWithFiltersOptions {
  source: "movie_listing" | "by_genre" | "by_actor" | "search";
  movie_id?: number;
  actor_id?: number;
  genre_id?: number;
  searchQuery?: string;
  initialPage?: number;
  limit?: number;
}

/**
 * Hook for fetching movies using BFF API with filter integration
 * This separates the data fetching from UI rendering concerns
 */
export const useMoviesWithFilters = (options: UseMoviesWithFiltersOptions) => {
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

  logger.debug("useMoviesWithFilters initialized", {
    source: options.source,
    actor_id: options.actor_id,
    genre_id: options.genre_id,
    searchQuery: options.searchQuery,
    filters: {
      imdb_rating,
      rotten_tomatoes_rating,
      metacritic_rating,
      year,
      sortOrder,
      sortDesc,
    },
  });

  // Build query key for React Query caching
  const queryKey = [
    "bff-movies",
    options.source,
    {
      actor_id: options.actor_id,
      genre_id: options.genre_id,
      searchQuery: options.searchQuery,
      // Include all filters in query key for proper invalidation
      imdb_rating,
      rotten_tomatoes_rating,
      metacritic_rating,
      year,
      sortOrder,
      sortDesc,
    },
  ];

  // Monitor for query key changes and invalidate when filters change
  useEffect(() => {
    logger.info("Filter changes detected, invalidating queries", {
      sortOrder,
      sortDesc,
      year,
      imdb_rating,
    });
    queryClient.invalidateQueries({ queryKey: ["bff-movies"] });
  }, [
    sortOrder,
    sortDesc,
    year,
    imdb_rating,
    rotten_tomatoes_rating,
    metacritic_rating,
    queryClient,
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
      logger.debug(`Fetching page ${pageParam} for source: ${options.source}`);

      switch (options.source) {
        case "movie_listing":
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
          return MovieAPI.getMovies({
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

        case "by_genre":
          if (!options.genre_id) {
            logger.error("genre_id is required for by_genre source");
            throw new Error("genre_id is required for by_genre source");
          }
          logger.info(
            `Fetching movies by genre via BFF API: ${options.genre_id}`
          );
          return MovieAPI.getMovies({
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

        case "by_actor":
          if (!options.actor_id) {
            logger.error("actor_id is required for by_actor source");
            throw new Error("actor_id is required for by_actor source");
          }
          logger.info(
            `Fetching movies by actor via BFF API: ${options.actor_id}`
          );
          return MovieAPI.getMoviesByActor(options.actor_id, {
            page: pageParam,
            limit: options.limit || 20,
            sort_by: sortOrder,
            sort_desc: sortDesc,
          });

        default:
          logger.error(`Unsupported source: ${options.source}`);
          throw new Error(`Unsupported source: ${options.source}`);
      }
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

  // Flatten all movies from all pages and ensure user interaction properties are initialized
  const movies: Movie[] = data?.pages
    ? ensureUserInteractions(data.pages.flatMap((page) => page.results))
    : [];

  // Get pagination info from the last page
  const lastPage = data?.pages?.[data.pages.length - 1];
  const totalMovies = lastPage?.total || 0;
  const currentPage = lastPage?.page || 1;

  // Log results or errors
  useEffect(() => {
    if (error) {
      logger.error("Error fetching movies via BFF:", error);
    } else if (movies.length > 0) {
      logger.info(
        `Fetched ${movies.length} movies from ${
          data?.pages?.length || 0
        } pages (total: ${totalMovies})`
      );

      // Log a sample movie to verify user interaction data
      if (movies[0]) {
        logger.debug("Sample movie with user interactions:", {
          id: movies[0].id,
          title: movies[0].title,
          watched: movies[0].watched,
          liked: movies[0].liked,
          in_watchlist: movies[0].in_watchlist,
        });
      }
    }
  }, [movies.length, totalMovies, data?.pages?.length, error]);

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

    // Raw data for advanced use cases
    rawData: data,
  };
};
