import { useQuery } from "@tanstack/react-query";
import { fetchData } from "../services/api-client";

export interface CastMember {
  id: number;
  name: string;
  character: string;
  profile_path?: string;
  profile_url?: string;
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
      return fetchData<MovieCastResponse>(`/movies/${id}/cast`);
    },
    staleTime: 1000 * 60 * 60, // 1 hour
    enabled: !!id,
  });
};

export default useMovieCast;
