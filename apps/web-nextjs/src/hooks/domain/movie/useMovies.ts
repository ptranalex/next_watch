"use client";

import { Movie } from "@/domain/entities";
import { MovieAPI, userInteractionAPI, UserMovieDetail } from "@/services/api";
import useMovieFilterStore from "@/store/movieFilterStore";
import {
  useInfiniteQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { useEffect } from "react";
import { createLogger } from "@/utils/logging";

// Create logger for this hook
const logger = createLogger("useMovies");

interface UseMoviesOptions {
  source:
    | "movie_listing"
    | "more_like_this"
    | "by_actor"
    | "watchlist"
    | "favorites"
    | "watched";
  movie_id?: number;
  actor_id?: number;
  genre_id?: number;
  page?: number;
  searchText?: string;
  // Legacy filter props (still available but ignored if store is used)
  imdb_rating?: number;
  rotten_tomatoes_rating?: number;
  metacritic_rating?: number;
  year?: number;
  sortOrder?: string;
  sortDesc?: boolean;
}

export const useMovies = (options: UseMoviesOptions) => {
  const queryClient = useQueryClient();

  // Get filters directly from the store
  const { filters } = useMovieFilterStore();

  // Use filter values from store, but allow override from props for backward compatibility
  const imdb_rating = filters.imdb_rating;
  const rotten_tomatoes_rating = filters.rotten_tomatoes_rating;
  const metacritic_rating = filters.metacritic_rating;
  const year = filters.year;
  const sortOrder = filters.sortOrder || "release_date";
  const sortDesc = true; // Always descending for now

  logger.debug("useMovies initialized with options", {
    source: options.source,
    movie_id: options.movie_id,
    actor_id: options.actor_id,
    genre_id: options.genre_id,
    filters: {
      imdb_rating,
      rotten_tomatoes_rating,
      metacritic_rating,
      year,
      sortOrder,
      sortDesc,
    },
  });

  const queryKey = [
    "movies",
    options.source,
    {
      movie_id: options.movie_id,
      actor_id: options.actor_id,
      genre_id: options.genre_id,
      // Add filter options to query key
      imdb_rating,
      rotten_tomatoes_rating,
      metacritic_rating,
      year,
      sortOrder,
      sortDesc,
    },
  ];

  // Monitor for query key changes
  useEffect(() => {
    // Force a refresh when sort order changes
    if (sortOrder) {
      logger.info(
        `Invalidating movies queries due to sort order change: ${sortOrder} (${
          sortDesc ? "descending" : "ascending"
        })`
      );
      queryClient.invalidateQueries({ queryKey: ["movies"] });
    }
  }, [sortOrder, sortDesc, queryClient]);

  const {
    data,
    isLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    error,
  } = useInfiniteQuery({
    queryKey,
    queryFn: async ({ pageParam }) => {
      const page = pageParam || 1;
      logger.debug(`Fetching page ${page} for source: ${options.source}`);

      switch (options.source) {
        case "movie_listing":
          logger.info(
            `Fetching movies list with filters: year=${year}, imdb=${imdb_rating}, sorting=${sortOrder}`
          );
          return MovieAPI.getMovies({
            page,
            limit: 10,
            genre_id: options.genre_id,
            actor_id: options.actor_id,
            sortBy: sortOrder,
            sort_desc: sortDesc,
            year,
            imdb_rating,
            rotten_tomatoes_rating,
            metacritic_rating,
          });
        case "more_like_this":
          if (!options.movie_id) {
            logger.error("movie_id is required for more_like_this source");
            throw new Error("movie_id is required for more_like_this");
          }
          logger.info(
            `Fetching related movies for movie_id: ${options.movie_id}`
          );
          return MovieAPI.getRelatedMovies(options.movie_id);
        case "by_actor":
          if (!options.actor_id) {
            logger.error("actor_id is required for by_actor source");
            throw new Error("actor_id is required for by_actor");
          }
          logger.info(
            `Fetching movies for actor_id: ${options.actor_id}, page: ${page}`
          );
          return MovieAPI.getMoviesByActor(options.actor_id, page);
        case "watchlist":
          // Use optimized endpoint to get watchlist with movie details in single API call
          if (page > 1) {
            logger.debug(
              "Watchlist source only supports page 1, returning empty array"
            );
            return { movies: [], total: 0, page };
          }

          logger.info("Fetching user's watchlist movies");
          const watchlistResponse = await userInteractionAPI.getUserMovies(
            "watchlist",
            20, // Use consistent page size with backend default
            0 // First page offset
          );

          // If no results, return empty array
          if (!watchlistResponse || watchlistResponse.length === 0) {
            logger.info("No watchlist movies found");
            return { movies: [], total: 0, page: 1 };
          }

          logger.info(
            `Found ${watchlistResponse.length} movies in user's watchlist`
          );
          // Transform the response to match expected format - API returns flattened structure
          const watchlistMovies = watchlistResponse.map(
            (item: UserMovieDetail) =>
              ({
                id: item.movie_id,
                title: item.title,
                poster_url: item.poster_url,
                poster_path: item.poster_url,
                release_date: item.release_date,
                imdb_rating: item.imdb_rating,
                // Map API response properties to expected Movie properties
                in_watchlist: item.in_watchlist,
                liked: item.liked,
                watched: item.watched,
              } as Movie)
          );

          return {
            movies: watchlistMovies,
            total: watchlistMovies.length,
            page: 1,
          };
        case "favorites":
          // Use optimized endpoint to get liked movies with details in single API call
          if (page > 1) {
            logger.debug(
              "Favorites source only supports page 1, returning empty array"
            );
            return { movies: [], total: 0, page };
          }

          logger.info("Fetching user's favorite (liked) movies");
          const likedResponse = await userInteractionAPI.getUserMovies(
            "liked",
            20, // Use consistent page size with backend default
            0 // First page offset
          );

          // If no results, return empty array
          if (!likedResponse || likedResponse.length === 0) {
            logger.info("No favorite movies found");
            return { movies: [], total: 0, page: 1 };
          }

          logger.info(
            `Found ${likedResponse.length} movies in user's favorites`
          );
          // Transform the response to match expected format - API returns flattened structure
          const favoriteMovies = likedResponse.map(
            (item: UserMovieDetail) =>
              ({
                id: item.movie_id,
                title: item.title,
                poster_url: item.poster_url,
                poster_path: item.poster_url,
                release_date: item.release_date,
                imdb_rating: item.imdb_rating,
                // Map API response properties to expected Movie properties
                in_watchlist: item.in_watchlist,
                liked: item.liked,
                watched: item.watched,
              } as Movie)
          );

          return {
            movies: favoriteMovies,
            total: favoriteMovies.length,
            page: 1,
          };
        case "watched":
          // Use optimized endpoint to get watched movies with details in single API call
          const pageSize = 20; // Default page size
          logger.info(
            `Fetching user's watched movies, page: ${page}, pageSize: ${pageSize}`
          );
          const watchedResponse = await userInteractionAPI.getUserMovies(
            "watched",
            pageSize, // Use fixed page size
            (page - 1) * pageSize // Calculate offset based on page number
          );

          // If no results, return empty array
          if (!watchedResponse || watchedResponse.length === 0) {
            logger.info(`No watched movies found for page ${page}`);
            return { movies: [], total: 0, page };
          }

          logger.info(
            `Found ${watchedResponse.length} watched movies for page ${page}`
          );
          // Transform the response to match expected format - API returns flattened structure
          const watchedMovies = watchedResponse.map(
            (item: UserMovieDetail) =>
              ({
                id: item.movie_id,
                title: item.title,
                poster_url: item.poster_url,
                poster_path: item.poster_url,
                release_date: item.release_date,
                imdb_rating: item.imdb_rating,
                // Map API response properties to expected Movie properties
                in_watchlist: item.in_watchlist,
                liked: item.liked,
                watched: item.watched,
              } as Movie)
          );

          return {
            movies: watchedMovies,
            total: 1000, // Set a large number to ensure hasNextPage is true if we have results
            page,
          };
        default:
          logger.error(`Unknown source: ${options.source}`);
          throw new Error(`Unknown source: ${options.source}`);
      }
    },
    getNextPageParam: (lastPage) => {
      if (!lastPage) return undefined;
      if (lastPage.movies.length === 0) return undefined;

      // Don't attempt to load more pages for watchlist and favorites
      if (options.source === "watchlist" || options.source === "favorites")
        return undefined;

      logger.debug(`Next page determined: ${lastPage.page + 1}`);
      return lastPage.page + 1;
    },
    staleTime: 5 * 60 * 1000,
    keepPreviousData: true,
    refetchOnWindowFocus: false,
  });

  // Log data updates
  useEffect(() => {
    if (data) {
      const totalMovies = data.pages.reduce(
        (sum, page) => sum + (page.movies?.length || 0),
        0
      );
      logger.info(
        `useMovies data updated: ${totalMovies} movies across ${data.pages.length} pages`
      );
    }
  }, [data]);

  // Log errors
  useEffect(() => {
    if (error) {
      logger.error("Error in useMovies hook:", error);
    }
  }, [error]);

  // User interaction mutation that updates UI only, not backend
  // The actual backend calls are handled in the MovieCard component
  const { mutate: updateMovie } = useMutation({
    mutationFn: (movie: Movie) => {
      // This is just an optimistic update handler - no actual API call here
      logger.debug(
        `Optimistic UI update for movie: ${movie.id} - ${movie.title}`
      );
      return Promise.resolve(movie);
    },
    onSuccess: (updatedMovie: Movie) => {
      if (!updatedMovie || typeof updatedMovie.id !== "number") {
        logger.warn("Invalid movie object provided to updateMovie");
        return;
      }

      // Find all pages that contain this movie
      interface QueryData {
        pages: Array<{
          movies: Movie[];
          [key: string]: unknown;
        }>;
        [key: string]: unknown;
      }

      queryClient.setQueriesData<QueryData>(
        { queryKey: ["movies"] },
        (oldData) => {
          if (!oldData) return oldData;

          logger.debug(`Updating movie ${updatedMovie.id} in query cache`);

          // Update each page that contains this movie
          const newData = {
            ...oldData,
            pages: oldData.pages.map((page) => {
              const movieIndex = page.movies.findIndex(
                (m) => m.id === updatedMovie.id
              );

              if (movieIndex >= 0) {
                logger.debug(
                  `Movie ${updatedMovie.id} found in page, updating`
                );
                // Create a new movies array with the updated movie
                const updatedMovies = [...page.movies];
                updatedMovies[movieIndex] = {
                  ...updatedMovies[movieIndex],
                  ...updatedMovie,
                };

                return {
                  ...page,
                  movies: updatedMovies,
                };
              }

              return page;
            }),
          };

          return newData;
        }
      );

      // Update the single movie cache as well if it exists
      queryClient.setQueryData(["movie", updatedMovie.id], (oldData: any) => {
        if (!oldData) return oldData;

        logger.debug(`Updating movie ${updatedMovie.id} in single movie cache`);
        return {
          ...oldData,
          ...updatedMovie,
        };
      });
    },
  });

  return {
    data,
    isLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    error,
    updateMovie,
  };
};
