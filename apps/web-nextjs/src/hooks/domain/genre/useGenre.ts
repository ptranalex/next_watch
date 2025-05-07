"use client";

import { toGenreEntity } from "@/domain/entities";
import { GenreAPI, MovieAPI, MovieListResponse } from "@/services/api";
import { useQuery } from "@tanstack/react-query";

/**
 * Hook for fetching and managing a single genre
 * @param id - Genre ID to fetch
 * @returns Genre data, loading state, error, and related information
 */
export function useGenre(id: number) {
  // Fetch genre data
  const {
    data: serviceGenre,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["genre", id],
    queryFn: () => GenreAPI.getById(id),
    enabled: !!id,
  });

  // Convert service genre to entity
  const genre = serviceGenre ? toGenreEntity(serviceGenre) : undefined;

  // Fetch movies in this genre
  const moviesQuery = useQuery<MovieListResponse>({
    queryKey: ["genreMovies", id],
    queryFn: () => MovieAPI.getMoviesByGenre(id),
    enabled: !!id,
  });

  return {
    genre,
    isLoading,
    error,
    movies: moviesQuery.data?.movies || [],
    totalMovies: moviesQuery.data?.total || 0,
  };
}

export default useGenre;
