import { useQuery } from "@tanstack/react-query";
import { MovieAPI } from "../services/movies-api";

/**
 * A hook that fetches movie details by ID
 * @param id The movie ID to fetch details for
 * @returns Query result with the movie details
 */
const useMovie = (id: number | string) => {
  return useQuery({
    queryKey: ["movie", id],
    queryFn: async () => {
      return MovieAPI.getById(Number(id));
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
    enabled: !!id,
  });
};

export default useMovie;
