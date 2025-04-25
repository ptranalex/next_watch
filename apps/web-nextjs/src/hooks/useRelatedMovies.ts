import { useQuery } from "@tanstack/react-query";
import { MovieListResponse } from "../services/movie-service";
import { fetchData } from "../services/api-client";

/**
 * A hook that fetches related movies for a given movie ID
 * @param id The movie ID to fetch related movies for
 * @param enabled Whether the query should be enabled or not
 * @returns Query result with related movies
 */
const useRelatedMovies = (id: number | string, enabled: boolean = true) => {
  return useQuery({
    queryKey: ["related-movies", id],
    queryFn: async () => {
      return fetchData<MovieListResponse>(`/movies/${id}/related`);
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
    enabled: !!id && enabled,
  });
};

export default useRelatedMovies;
