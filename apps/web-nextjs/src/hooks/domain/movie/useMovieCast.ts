import { MovieAPI } from "@/services/api";
import { useQuery } from "@tanstack/react-query";

export const useMovieCast = (movieId: number) => {
  return useQuery({
    queryKey: ["movieCast", movieId],
    queryFn: () => MovieAPI.getCast(movieId),
  });
};
