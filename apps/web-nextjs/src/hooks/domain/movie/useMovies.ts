"use client";

import {
  useInfiniteQuery,
  useMutation,
  useQueryClient,
  UseInfiniteQueryResult,
} from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { MovieAPI, MovieListResponse } from "@/services/api";
import { Movie } from "@/domain/entities";
import { useEffect } from "react";
import { userInteractionAPI } from "@/services/api";

interface UseMoviesOptions {
  source: "movie_listing" | "more_like_this" | "by_actor";
  movie_id?: number;
  actor_id?: number;
  genre_id?: number;
  page?: number;
  searchText?: string;
}

export const useMovies = (options: UseMoviesOptions) => {
  const queryClient = useQueryClient();
  const searchParams = useSearchParams();

  // Read filter values directly from URL
  const imdb_rating = searchParams.get("imdb")
    ? Number(searchParams.get("imdb"))
    : undefined;
  const rotten_tomatoes_rating = searchParams.get("rt")
    ? Number(searchParams.get("rt"))
    : undefined;
  const metacritic_rating = searchParams.get("mc")
    ? Number(searchParams.get("mc"))
    : undefined;
  const year = searchParams.get("year")
    ? Number(searchParams.get("year"))
    : undefined;
  const sortOrder = searchParams.get("sort") || "release_date";
  const sortDesc = searchParams.get("desc") !== "false"; // Default to true unless explicitly false

  // Log filter values to verify they're being read from URL
  console.log("Filter values from URL:", {
    imdb_rating,
    rotten_tomatoes_rating,
    metacritic_rating,
    year,
    sortOrder,
    sortDesc,
    allParams: {
      sort: searchParams.get("sort"),
      desc: searchParams.get("desc"),
      imdb: searchParams.get("imdb"),
      rt: searchParams.get("rt"),
      mc: searchParams.get("mc"),
      year: searchParams.get("year"),
    },
  });

  const queryKey = [
    "movies",
    options.source,
    {
      movie_id: options.movie_id,
      actor_id: options.actor_id,
      genre_id: options.genre_id,
      // Add URL filters to query key to trigger refetch when URL changes
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
    console.log("useMovies - QueryKey changed:", {
      sortOrder,
      sortDesc,
    });
    // Force a refresh when sort order changes
    if (sortOrder) {
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

      console.log("Making API call with filters:", {
        page,
        imdb_rating,
        rotten_tomatoes_rating,
        metacritic_rating,
        year,
        sortOrder,
        sortDesc,
      });

      switch (options.source) {
        case "movie_listing":
          console.log("useMovies - Calling MovieAPI.getMovies with sort:", {
            sortBy: sortOrder,
            sort_desc: sortDesc,
          });
          return MovieAPI.getMovies({
            page,
            limit: 50,
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
          if (!options.movie_id)
            throw new Error("movie_id is required for more_like_this");
          return MovieAPI.getRelatedMovies(options.movie_id);
        case "by_actor":
          if (!options.actor_id)
            throw new Error("actor_id is required for by_actor");
          return MovieAPI.getMoviesByActor(options.actor_id, page);
        default:
          throw new Error(`Unknown source: ${options.source}`);
      }
    },
    getNextPageParam: (lastPage) => {
      if (!lastPage) return undefined;
      if (lastPage.movies.length === 0) return undefined;
      return lastPage.page + 1;
    },
    staleTime: 5 * 60 * 1000,
    keepPreviousData: true,
    refetchOnWindowFocus: false,
  });

  // User interaction mutation that updates UI only, not backend
  // The actual backend calls are handled in the MovieCard component
  const { mutate: updateMovie } = useMutation({
    mutationFn: (movie: Movie) => {
      // This is just an optimistic update handler - no actual API call here
      return Promise.resolve(movie);
    },
    onSuccess: (updatedMovie: Movie) => {
      if (!updatedMovie || typeof updatedMovie.id !== "number") {
        console.error("Invalid movie for update:", updatedMovie);
        return;
      }

      // Update local cache with the optimistic update
      queryClient.setQueryData(queryKey, (oldData: any) => {
        if (!oldData) return oldData;
        return {
          ...oldData,
          pages: oldData.pages.map((page: any) => ({
            ...page,
            movies: page.movies.map((m: Movie) =>
              m.id === updatedMovie.id ? { ...m, ...updatedMovie } : m
            ),
          })),
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
    updateMovie,
    error,
  };
};
