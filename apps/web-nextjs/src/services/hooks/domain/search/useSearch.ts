import { useDebounce } from "@/services/hooks/ui/useDebounce";
import { SearchAPI, MovieSearchResponse } from "@/services/api";
import { useQuery, useInfiniteQuery } from "@tanstack/react-query";
import { Movie } from "@/domain/entities";

interface UseSearchOptions {
  query: string;
  page?: number;
  actorId?: number;
  genreId?: number;
  sortBy?: string;
  sortDesc?: boolean;
  imdbRating?: number;
  rottenTomatoesRating?: number;
  metacriticRating?: number;
  year?: number;
  startYear?: number;
  endYear?: number;
  userId?: number;
}

export function useSearch({
  query,
  page = 1,
  actorId,
  genreId,
  sortBy,
  sortDesc,
  imdbRating,
  rottenTomatoesRating,
  metacriticRating,
  year,
  startYear,
  endYear,
  userId,
}: UseSearchOptions) {
  const debouncedQuery = useDebounce(query, 500);

  const { data, error, isLoading, isFetching } = useQuery<MovieSearchResponse>({
    queryKey: [
      "search",
      debouncedQuery,
      page,
      actorId,
      genreId,
      sortBy,
      sortDesc,
      imdbRating,
      rottenTomatoesRating,
      metacriticRating,
      year,
      startYear,
      endYear,
      userId,
    ],
    queryFn: () =>
      SearchAPI.searchMovies({
        q: debouncedQuery,
        page,
        actor_id: actorId,
        genre_id: genreId,
        sort_by: sortBy,
        sort_desc: sortDesc,
        imdb_rating: imdbRating,
        rotten_tomatoes_rating: rottenTomatoesRating,
        metacritic_rating: metacriticRating,
        year,
        start_year: startYear,
        end_year: endYear,
        user_id: userId,
      }),
    enabled: debouncedQuery.length > 0,
  });

  return {
    results: data?.results || [],
    total: data?.total_count || 0,
    query: data?.query || debouncedQuery,
    hasNext: data?.has_next || false,
    currentPage: data?.page || page,
    error,
    isLoading,
    isFetching,
  };
}

interface UseInfiniteSearchOptions {
  query: string;
  actorId?: number;
  genreId?: number;
  sortBy?: string;
  sortDesc?: boolean;
  imdbRating?: number;
  rottenTomatoesRating?: number;
  metacriticRating?: number;
  year?: number;
  startYear?: number;
  endYear?: number;
  userId?: number;
}

export function useInfiniteSearch({
  query,
  actorId,
  genreId,
  sortBy,
  sortDesc,
  imdbRating,
  rottenTomatoesRating,
  metacriticRating,
  year,
  startYear,
  endYear,
  userId,
}: UseInfiniteSearchOptions) {
  const debouncedQuery = useDebounce(query, 500);

  const {
    data,
    error,
    isLoading,
    isFetching,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
  } = useInfiniteQuery<MovieSearchResponse>({
    queryKey: [
      "infinite-search",
      debouncedQuery,
      actorId,
      genreId,
      sortBy,
      sortDesc,
      imdbRating,
      rottenTomatoesRating,
      metacriticRating,
      year,
      startYear,
      endYear,
      userId,
    ],
    queryFn: ({ pageParam = 1 }) =>
      SearchAPI.searchMovies({
        q: debouncedQuery,
        page: pageParam,
        actor_id: actorId,
        genre_id: genreId,
        sort_by: sortBy,
        sort_desc: sortDesc,
        imdb_rating: imdbRating,
        rotten_tomatoes_rating: rottenTomatoesRating,
        metacritic_rating: metacriticRating,
        year,
        start_year: startYear,
        end_year: endYear,
        user_id: userId,
      }),
    getNextPageParam: (lastPage) => {
      return lastPage.has_next ? lastPage.page + 1 : undefined;
    },
    enabled: debouncedQuery.length > 0,
  });

  // Flatten all pages into a single array of movies
  const movies: Movie[] = data?.pages.flatMap((page) => page.results) || [];
  const totalMovies = data?.pages[0]?.total_count || 0;
  const fetchedMoviesCount = movies.length;

  return {
    movies,
    totalMovies,
    fetchedMoviesCount,
    query: debouncedQuery,
    hasNextPage,
    fetchNextPage,
    error,
    isLoading,
    isFetching,
    isFetchingNextPage,
  };
}
