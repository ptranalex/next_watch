import { useQuery } from "@tanstack/react-query";
import { Movie } from "../services/movie-service";
import { fetchData } from "../services/api-client";

/**
 * A hook that fetches movie details by ID
 * @param id The movie ID to fetch details for
 * @returns Query result with the movie details
 */
const useMovie = (id: number | string) => {
  return useQuery({
    queryKey: ["movie", id],
    queryFn: async () => {
      return fetchData<Movie>(`/movies/${id}`);
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
    enabled: !!id,
  });
};

export default useMovie;
