import { useQuery } from "@tanstack/react-query";
import { MovieListResponse } from "../services/movie-service";

/**
 * A hook that fetches related movies for a given movie ID
 * @param id The movie ID to fetch related movies for
 * @returns Query result with related movies
 */
const useRelatedMovies = (id: number | string) => {
  return useQuery({
    queryKey: ["related-movies", id],
    queryFn: async () => {
      const response = await fetch(
        `http://localhost:8000/movies/${id}/related`
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch related movies for ID ${id}`);
      }

      const data = await response.json();
      return data as MovieListResponse;
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
    enabled: !!id,
  });
};

export default useRelatedMovies;
