"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  MovieAPI,
  MovieCastResponse,
  userInteractionAPI,
  UserMovieInteractionResponse,
} from "@/services/api";
import { Movie, toMovieEntity } from "@/domain/entities";
import { FEATURES } from "@/config/features";
import { useAuth } from "@/hooks";

/**
 * Hook for fetching and managing a single movie
 * @param id - Movie ID to fetch
 * @returns Movie data, loading state, error, and update mutation functions
 */
export function useMovie(id: number) {
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuth();

  // Fetch movie data
  const {
    data: serviceMovie,
    isLoading: isLoadingMovie,
    error: movieError,
  } = useQuery({
    queryKey: ["movie", id],
    queryFn: () => MovieAPI.getById(id),
    enabled: !!id,
  });

  // Fetch user interaction data if authenticated
  const {
    data: interactionData,
    isLoading: isLoadingInteraction,
    error: interactionError,
  } = useQuery({
    queryKey: ["movieInteraction", id],
    queryFn: () => userInteractionAPI.getMovieInteraction(id),
    enabled: !!id && isAuthenticated,
    onSuccess: (data) => {
      console.log("Loaded interaction data:", data);
      // Debug API property mapping
      if (data) {
        console.log("API property values:", {
          liked: data.liked,
          watched: data.watched,
          in_watchlist: data.in_watchlist,
        });
      }
    },
    onError: (error) => {
      console.error("Error loading interaction data:", error);
    },
  });

  // Combine movie data with user interaction data
  const movie = serviceMovie
    ? {
        ...toMovieEntity(serviceMovie),
        // Apply user interaction properties if available
        ...(interactionData && {
          liked: interactionData.liked,
          watched: interactionData.watched,
          in_watchlist: interactionData.in_watchlist,
        }),
      }
    : undefined;

  // Log the combined movie data
  if (movie) {
    // Cast to any to avoid TypeScript errors for debugging logs
    const movieData = movie as any;
    console.log("Combined movie data:", {
      id: movieData.id,
      title: movieData.title,
      liked: movieData.liked,
      watched: movieData.watched,
      in_watchlist: movieData.in_watchlist,
    });
  }

  // Combined loading state
  const isLoading = isLoadingMovie || (isAuthenticated && isLoadingInteraction);

  // Combined error
  const error = movieError || (isAuthenticated ? interactionError : null);

  // Toggle watched status
  const { mutate: toggleWatched } = useMutation({
    mutationFn: async () => {
      if (!movie) throw new Error("Movie not loaded");

      // Call the API and return an optimistic update of the movie
      await userInteractionAPI.toggleWatched(id);
      return { ...movie, watched: !movie.watched };
    },
    onSuccess: (updatedMovie) => {
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
  });

  // Toggle liked status
  const { mutate: toggleLiked } = useMutation({
    mutationFn: async () => {
      if (!movie) throw new Error("Movie not loaded");

      // Call the API and return an optimistic update of the movie
      await userInteractionAPI.toggleLiked(id);
      return { ...movie, liked: !movie.liked };
    },
    onSuccess: (updatedMovie) => {
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
  });

  // Toggle in_watchlist status
  const { mutate: toggleInWatchlist } = useMutation({
    mutationFn: async () => {
      if (!movie) throw new Error("Movie not loaded");

      // Call the API and return an optimistic update of the movie
      await userInteractionAPI.toggleWatchlist(id);
      return { ...movie, in_watchlist: !movie.in_watchlist };
    },
    onSuccess: (updatedMovie) => {
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
          return MovieAPI.getMoviesByGenre(firstGenre.id);
        }
      }
      return { movies: [], total: 0, page: 1, page_size: 20 };
    },
    enabled: FEATURES.SHOW_MORE_LIKE_THIS && !!serviceMovie,
  });

  // Fetch movie cast
  const castQuery = useQuery<MovieCastResponse>({
    queryKey: ["movieCast", id],
    queryFn: () => MovieAPI.getCast(id),
  });

  return {
    movie,
    isLoading,
    error,
    toggleWatched,
    toggleLiked,
    toggleWatchlist: toggleInWatchlist,
    relatedMovies: relatedMoviesQuery.data,
    cast: castQuery.data?.cast || [],
  };
}
