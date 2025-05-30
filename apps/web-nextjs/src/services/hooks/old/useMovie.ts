"use client";

import { FEATURES } from "@/config/features";
import { toMovieEntity, Movie } from "@/domain/entities";
import { useAuth } from "@/services/hooks";
import {
  MovieAPI,
  MovieCastResponse,
  userInteractionAPI,
  UserMovieInteractionResponse,
} from "@/services/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createLogger } from "@/utils/logging";

// Create logger for this hook
const logger = createLogger("useMovie");

/**
 * Hook for fetching and managing a single movie
 * @param id - Movie ID to fetch
 * @returns Movie data, loading state, error, and update mutation functions
 */
export function useMovie(id: number) {
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuth();

  // Log hook initialization
  logger.debug(
    `useMovie initialized with id: ${id}, authenticated: ${isAuthenticated}`
  );

  // Fetch movie data
  const {
    data: serviceMovie,
    isLoading: isLoadingMovie,
    error: movieError,
    refetch: refetchMovie,
  } = useQuery({
    queryKey: ["movie", id],
    queryFn: () => MovieAPI.getById(id),
    enabled: id > 0,
  });

  // Fetch user interaction data if authenticated
  const {
    data: interactionData,
    isLoading: isLoadingInteraction,
    error: interactionError,
    refetch: refetchInteraction,
  } = useQuery({
    queryKey: ["movieInteraction", id],
    queryFn: () => userInteractionAPI.getMovieInteraction(id),
    enabled: id > 0 && isAuthenticated,
    onSuccess: (data) => {
      logger.info("Loaded interaction data for movie", {
        movieId: id,
        liked: data?.liked,
        watched: data?.watched,
        in_watchlist: data?.in_watchlist,
      });
    },
    onError: (error) => {
      logger.error(`Error loading interaction data for movie ${id}:`, error);
    },
  });

  // Combine movie data with user interaction data
  const movie = serviceMovie
    ? ({
        ...toMovieEntity(serviceMovie),
        // Apply user interaction properties if available
        ...(interactionData && {
          liked: interactionData.liked,
          watched: interactionData.watched,
          in_watchlist: interactionData.in_watchlist,
        }),
      } as Movie)
    : undefined;

  // Log the combined movie data
  if (movie) {
    logger.debug("Combined movie data", {
      id: movie.id,
      title: movie.title,
      liked: movie.liked,
      watched: movie.watched,
      in_watchlist: movie.in_watchlist,
    });
  }

  // Combined loading state
  const isLoading = isLoadingMovie || (isAuthenticated && isLoadingInteraction);

  // Combined error
  const error = movieError || (isAuthenticated ? interactionError : null);

  // Log errors
  if (error) {
    logger.error(`Error in useMovie hook for movie ${id}:`, error);
  }

  // Refetch all movie data
  const refetch = async () => {
    logger.info(`Refetching movie data for ID: ${id}`);

    try {
      // Refetch movie data
      await refetchMovie();

      // Refetch interaction data if authenticated
      if (isAuthenticated) {
        await refetchInteraction();
      }

      logger.info(`Refetch complete for movie ID: ${id}`);
    } catch (error) {
      logger.error(`Error during refetch for movie ${id}:`, error);
    }
  };

  // Toggle watched status
  const { mutate: toggleWatched } = useMutation({
    mutationFn: async () => {
      if (!movie) throw new Error("Movie not loaded");

      const movieTitle = (movie as Movie).title || "Unknown movie";
      logger.info(`Toggling watched status for movie: ${id} - ${movieTitle}`);

      // Call the API and return an optimistic update of the movie
      await userInteractionAPI.toggleWatched(id);
      return { ...movie, watched: !movie.watched };
    },
    onSuccess: (updatedMovie) => {
      logger.info(
        `Updated watched status for movie ${id}: ${updatedMovie.watched}`
      );

      // Update the movie interaction in the cache
      queryClient.setQueryData<UserMovieInteractionResponse | null>(
        ["movieInteraction", id],
        (oldData) => {
          if (!oldData) {
            return {
              id: 0, // Will be set by backend
              user_id: 0, // Will be set by backend
              movie_id: id,
              watched: updatedMovie.watched || false,
              liked: updatedMovie.liked || false,
              in_watchlist: updatedMovie.in_watchlist || false,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            };
          }
          return { ...oldData, watched: updatedMovie.watched };
        }
      );
    },
    onError: (error) => {
      logger.error(`Error toggling watched status for movie ${id}:`, error);
    },
  });

  // Toggle liked status
  const { mutate: toggleLiked } = useMutation({
    mutationFn: async () => {
      if (!movie) throw new Error("Movie not loaded");

      const movieTitle = (movie as Movie).title || "Unknown movie";
      logger.info(`Toggling liked status for movie: ${id} - ${movieTitle}`);

      // Call the API and return an optimistic update of the movie
      await userInteractionAPI.toggleLiked(id);
      return { ...movie, liked: !movie.liked };
    },
    onSuccess: (updatedMovie) => {
      logger.info(
        `Updated liked status for movie ${id}: ${updatedMovie.liked}`
      );

      // Update the movie interaction in the cache
      queryClient.setQueryData<UserMovieInteractionResponse | null>(
        ["movieInteraction", id],
        (oldData) => {
          if (!oldData) {
            return {
              id: 0, // Will be set by backend
              user_id: 0, // Will be set by backend
              movie_id: id,
              watched: updatedMovie.watched || false,
              liked: updatedMovie.liked || false,
              in_watchlist: updatedMovie.in_watchlist || false,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            };
          }
          return { ...oldData, liked: updatedMovie.liked };
        }
      );
    },
    onError: (error) => {
      logger.error(`Error toggling liked status for movie ${id}:`, error);
    },
  });

  // Toggle in_watchlist status
  const { mutate: toggleInWatchlist } = useMutation({
    mutationFn: async () => {
      if (!movie) throw new Error("Movie not loaded");

      const movieTitle = (movie as Movie).title || "Unknown movie";
      logger.info(`Toggling watchlist status for movie: ${id} - ${movieTitle}`);

      // Call the API and return an optimistic update of the movie
      await userInteractionAPI.toggleWatchlist(id);
      return { ...movie, in_watchlist: !movie.in_watchlist };
    },
    onSuccess: (updatedMovie) => {
      logger.info(
        `Updated watchlist status for movie ${id}: ${updatedMovie.in_watchlist}`
      );

      // Update the movie interaction in the cache
      queryClient.setQueryData<UserMovieInteractionResponse | null>(
        ["movieInteraction", id],
        (oldData) => {
          if (!oldData) {
            return {
              id: 0, // Will be set by backend
              user_id: 0, // Will be set by backend
              movie_id: id,
              watched: updatedMovie.watched || false,
              liked: updatedMovie.liked || false,
              in_watchlist: updatedMovie.in_watchlist || false,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            };
          }
          return { ...oldData, in_watchlist: updatedMovie.in_watchlist };
        }
      );
    },
    onError: (error) => {
      logger.error(`Error toggling watchlist status for movie ${id}:`, error);
    },
  });

  // Fetch related movies (similar genres)
  const relatedMoviesQuery = useQuery({
    queryKey: ["relatedMovies", id],
    queryFn: async () => {
      if (serviceMovie?.genres && Array.isArray(serviceMovie.genres)) {
        // Type check to ensure it's actually a Genre object with an id
        const firstGenre = serviceMovie.genres[0];
        if (
          firstGenre &&
          typeof firstGenre === "object" &&
          "id" in firstGenre
        ) {
          logger.debug(
            `Fetching related movies by genre ${firstGenre.id} for movie ${id}`
          );
          return MovieAPI.getMoviesByGenre(firstGenre.id);
        }
      }

      logger.debug(
        `No genres found for movie ${id}, skipping related movies fetch`
      );
      return { movies: [], total: 0, page: 1, page_size: 20 };
    },
    enabled: FEATURES.SHOW_MORE_LIKE_THIS && !!serviceMovie && id > 0,
    onSuccess: (data) => {
      logger.info(
        `Fetched ${data.movies.length} related movies for movie ${id}`
      );
    },
    onError: (error) => {
      logger.error(`Error fetching related movies for movie ${id}:`, error);
    },
  });

  // Fetch movie cast
  const castQuery = useQuery<MovieCastResponse>({
    queryKey: ["movieCast", id],
    queryFn: () => MovieAPI.getCast(id),
    enabled: id > 0,
    onSuccess: (data) => {
      logger.info(
        `Fetched ${data.cast?.length || 0} cast members for movie ${id}`
      );
    },
    onError: (error) => {
      logger.error(`Error fetching cast for movie ${id}:`, error);
    },
  });

  return {
    movie,
    isLoading,
    error,
    toggleWatched,
    toggleLiked,
    toggleWatchlist: toggleInWatchlist,
    refetch,
    relatedMovies: relatedMoviesQuery.data,
    cast: castQuery.data?.cast || [],
  };
}
