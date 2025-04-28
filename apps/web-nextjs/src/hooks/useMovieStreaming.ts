import { useQuery } from "@tanstack/react-query";
import { MovieAPI } from "../services/movies-api";

/**
 * A hook that fetches streaming sources for a movie
 * @param id The movie ID to fetch streaming sources for
 * @returns Query result with streaming sources
 */
const useMovieStreaming = (id: number | string) => {
  return useQuery({
    queryKey: ["movie-streaming", id],
    queryFn: async () => {
      return MovieAPI.getStreamingSources(Number(id));
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
    enabled: !!id,
  });
};

export default useMovieStreaming;
