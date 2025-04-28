"use client";

import { useState, useEffect } from "react";

interface Movie {
  id: string;
  title: string;
  poster_path: string;
  vote_average: number;
  release_date: string;
  genres?: string[];
}

interface MoviesResponse {
  results: Movie[];
  page: number;
  total_pages: number;
  total_results: number;
}

interface UseMoviesOptions {
  genre?: string;
  searchQuery?: string;
  sortBy?: string;
  minRating?: number;
  maxRating?: number;
  year?: number;
}

export function useMovies(options: UseMoviesOptions = {}) {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);

  // Reset everything when search params change
  useEffect(() => {
    setMovies([]);
    setPage(1);
    setHasMore(false);
    fetchMovies(1);
  }, [
    options.genre,
    options.searchQuery,
    options.sortBy,
    options.minRating,
    options.maxRating,
    options.year,
  ]);

  // Function to fetch movies from the API
  const fetchMovies = async (pageToFetch: number) => {
    if (pageToFetch === 1) {
      setIsLoading(true);
      setError(null);
    } else {
      setIsLoadingMore(true);
    }

    try {
      // In a real app, this would be an API call
      // Example: const response = await apiClient.get<MoviesResponse>('/movies', { params: { ...options, page: pageToFetch } });

      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Mock data
      const mockResponse: MoviesResponse = {
        results: Array(20)
          .fill(0)
          .map((_, index) => ({
            id: `${(pageToFetch - 1) * 20 + index + 1}`,
            title: `Sample Movie ${(pageToFetch - 1) * 20 + index + 1}`,
            poster_path: `https://via.placeholder.com/300x450?text=Movie${
              (pageToFetch - 1) * 20 + index + 1
            }`,
            vote_average: Math.floor(Math.random() * 10) + 1,
            release_date: `${2000 + Math.floor(Math.random() * 23)}-${String(
              Math.floor(Math.random() * 12) + 1
            ).padStart(2, "0")}-${String(
              Math.floor(Math.random() * 28) + 1
            ).padStart(2, "0")}`,
            genres: ["Action", "Adventure", "Drama", "Comedy", "Thriller"]
              .sort(() => 0.5 - Math.random())
              .slice(0, 2),
          })),
        page: pageToFetch,
        total_pages: 5,
        total_results: 100,
      };

      // Filter by genre if specified
      if (options.genre) {
        mockResponse.results = mockResponse.results.filter((movie) =>
          movie.genres?.includes(options.genre!)
        );
      }

      // Filter by search query if specified
      if (options.searchQuery) {
        mockResponse.results = mockResponse.results.filter((movie) =>
          movie.title.toLowerCase().includes(options.searchQuery!.toLowerCase())
        );
      }

      // Apply other filters as needed...

      if (pageToFetch === 1) {
        setMovies(mockResponse.results);
      } else {
        setMovies((prev) => [...prev, ...mockResponse.results]);
      }

      setHasMore(pageToFetch < mockResponse.total_pages);
      setPage(pageToFetch);
    } catch (err) {
      setError(
        err instanceof Error ? err : new Error("Unknown error occurred")
      );
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
    }
  };

  // Function to load more movies
  const loadMore = () => {
    if (!isLoadingMore && hasMore) {
      fetchMovies(page + 1);
    }
  };

  return {
    movies,
    isLoading,
    error,
    loadMore,
    hasMore,
    isLoadingMore,
  };
}
