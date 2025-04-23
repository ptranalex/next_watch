import { useQuery } from "@tanstack/react-query";
import { Movie } from "../services/movie-service";

/**
 * A hook that fetches movie details by ID
 * @param id The movie ID to fetch details for
 * @returns Query result with the movie details
 */
const useMovie = (id: number | string) => {
  return useQuery({
    queryKey: ["movie", id],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8000/movies/${id}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch movie details for ID ${id}`);
      }

      const data = await response.json();
      return data as Movie;
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
    enabled: !!id,
  });
};

export default useMovie;
