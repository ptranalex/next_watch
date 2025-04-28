import { useQuery } from "@tanstack/react-query";
import { MovieAPI } from "../services/movies-api";

export interface CastMember {
  id: number;
  actor_id: number;
  name: string;
  character?: string;
  profile_path?: string;
  profile_url?: string;
  order?: number;
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
      return MovieAPI.getCast(Number(id));
    },
    staleTime: 1000 * 60 * 60, // 1 hour
    enabled: !!id,
  });
};

export default useMovieCast;
