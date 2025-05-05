import { useQuery } from "@tanstack/react-query";
import { MovieAPI, MovieListResponse } from "@/services/api";
import { useDebounce } from "../ui/useDebounce";

interface UseSearchOptions {
  query: string;
  page?: number;
  actorId?: number;
  genreId?: number;
}

export function useSearch({
  query,
  page = 1,
  actorId,
  genreId,
}: UseSearchOptions) {
  const debouncedQuery = useDebounce(query, 500);

  const { data, error, isLoading, isFetching } = useQuery<MovieListResponse>({
    queryKey: ["search", debouncedQuery, page, actorId, genreId],
    queryFn: () =>
      MovieAPI.search(debouncedQuery, {
        page,
        actor_id: actorId,
        genre_id: genreId,
      }),
    enabled: debouncedQuery.length > 0,
  });

  return {
    results: data?.movies || [],
    total: data?.total || 0,
    error,
    isLoading,
    isFetching,
  };
}
