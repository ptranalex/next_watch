import { useQuery } from "@tanstack/react-query";
import { fetchData } from "@/services/api";

export interface Trailer {
  id: number;
  movie_id: number;
  youtube_key: string;
  name: string;
  is_official: boolean;
  url_link?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Hook to fetch movie trailers
 * @param movieId - The movie ID to fetch trailers for
 * @returns Query result with trailers data
 */
export function useMovieTrailer(movieId: number) {
  // Validate movie ID
  const isValidId = typeof movieId === "number" && movieId > 0;

  return useQuery<Trailer[]>({
    queryKey: ["movie", movieId, "trailers"],
    queryFn: async () => {
      if (!isValidId) {
        console.warn(
          `Invalid movie ID provided to useMovieTrailer: ${movieId}`
        );
        return [];
      }

      try {
        const trailers = await fetchData<Trailer[]>(
          `/api/v1/movies/${movieId}/trailers`
        );

        // Validate the response
        if (!Array.isArray(trailers)) {
          console.error("Invalid trailers response format:", trailers);
          return [];
        }

        // Filter out invalid trailer entries
        return trailers.filter(
          (trailer) =>
            trailer &&
            typeof trailer === "object" &&
            typeof trailer.youtube_key === "string" &&
            trailer.youtube_key.length > 0
        );
      } catch (error) {
        console.error(
          `Error fetching trailers for movie ID ${movieId}:`,
          error
        );
        throw error;
      }
    },
    enabled: isValidId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });
}
