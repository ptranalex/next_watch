import { useQuery } from "@tanstack/react-query";
import { MovieAPI } from "@/services/api";

export const useMovieCast = (movieId: number) => {
  return useQuery({
    queryKey: ["movieCast", movieId],
    queryFn: () => MovieAPI.getCast(movieId),
  });
};
