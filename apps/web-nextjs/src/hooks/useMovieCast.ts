import { useQuery } from "@tanstack/react-query";

export interface CastMember {
  id: number;
  name: string;
  character: string;
  profile_path?: string;
  order: number;
}

interface MovieCastResponse {
  cast: CastMember[];
  movie_id: number;
}

/**
 * A hook that fetches cast information for a given movie ID
 * @param id The movie ID to fetch cast for
 * @returns Query result with cast members
 */
const useMovieCast = (id: number | string) => {
  return useQuery({
    queryKey: ["movie-cast", id],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8000/movies/${id}/cast`);

      if (!response.ok) {
        throw new Error(`Failed to fetch cast for movie ID ${id}`);
      }

      const data = await response.json();
      return data as MovieCastResponse;
    },
    staleTime: 1000 * 60 * 60, // 1 hour
    enabled: !!id,
  });
};

export default useMovieCast;
