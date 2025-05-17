"use client";

import { toGenreEntity } from "@/domain/entities";
import { GenreAPI, MovieAPI, MovieListResponse } from "@/services/api";
import { useQuery } from "@tanstack/react-query";
import { createLogger } from "@/utils/logging";
import { useEffect } from "react";

// Create logger for this hook
const logger = createLogger("useGenre");

/**
 * Hook for fetching and managing a single genre
 * @param id - Genre ID to fetch
 * @returns Genre data, loading state, error, and related information
 */
export function useGenre(id: number) {
  // Log hook initialization
  logger.debug(`useGenre initialized with id: ${id}`);

  // Fetch genre data
  const {
    data: serviceGenre,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["genre", id],
    queryFn: () => {
      logger.info(`Fetching genre data for id: ${id}`);
      return GenreAPI.getById(id);
    },
    enabled: !!id,
  });

  // Convert service genre to entity
  const genre = serviceGenre ? toGenreEntity(serviceGenre) : undefined;

  // Log when genre data is received
  useEffect(() => {
    if (serviceGenre) {
      logger.info(`Genre data loaded: ${serviceGenre.name} (id: ${id})`);
    }
  }, [serviceGenre, id]);

  // Fetch movies in this genre
  const moviesQuery = useQuery<MovieListResponse>({
    queryKey: ["genreMovies", id],
    queryFn: () => {
      logger.info(`Fetching movies for genre id: ${id}`);
      return MovieAPI.getMoviesByGenre(id);
    },
    enabled: !!id,
    onSuccess: (data) => {
      logger.info(
        `Fetched ${data.movies?.length || 0} movies for genre ${
          genre?.name || id
        }`
      );
    },
  });

  // Log errors
  useEffect(() => {
    if (error) {
      logger.error(`Error fetching genre data for id ${id}:`, error);
    }
    if (moviesQuery.error) {
      logger.error(
        `Error fetching genre movies for id ${id}:`,
        moviesQuery.error
      );
    }
  }, [error, moviesQuery.error, id]);

  return {
    genre,
    isLoading,
    error,
    movies: moviesQuery.data?.movies || [],
    totalMovies: moviesQuery.data?.total || 0,
  };
}

export default useGenre;
