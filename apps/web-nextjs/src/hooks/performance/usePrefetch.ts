"use client";

import { useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { GenreAPI, ActorAPI, MovieAPI } from "@/services/api";

/**
 * Hook to provide prefetching capabilities for common entity types
 * This improves UX by loading data in advance of navigation
 */
export function usePrefetch() {
  const queryClient = useQueryClient();

  /**
   * Prefetch a genre and its movies
   */
  const prefetchGenre = useCallback(
    (genreId: number) => {
      // Prefetch the genre itself
      queryClient.prefetchQuery({
        queryKey: ["genre", genreId],
        queryFn: () => GenreAPI.getById(genreId),
      });

      // Prefetch movies for this genre
      queryClient.prefetchQuery({
        queryKey: ["genreMovies", genreId],
        queryFn: () => MovieAPI.getMoviesByGenre(genreId),
      });
    },
    [queryClient]
  );

  /**
   * Prefetch an actor and their movies
   */
  const prefetchActor = useCallback(
    (actorId: number) => {
      // Prefetch the actor itself
      queryClient.prefetchQuery({
        queryKey: ["actor", actorId],
        queryFn: () => ActorAPI.getById(actorId),
      });

      // Prefetch movies for this actor
      queryClient.prefetchQuery({
        queryKey: ["actorMovies", actorId],
        queryFn: () => ActorAPI.getActorMovies(actorId),
      });
    },
    [queryClient]
  );

  /**
   * Prefetch a movie's details
   */
  const prefetchMovie = useCallback(
    (movieId: number) => {
      queryClient.prefetchQuery({
        queryKey: ["movie", movieId],
        queryFn: () => MovieAPI.getById(movieId),
      });
    },
    [queryClient]
  );

  return {
    prefetchGenre,
    prefetchActor,
    prefetchMovie,
  };
}

export default usePrefetch;
