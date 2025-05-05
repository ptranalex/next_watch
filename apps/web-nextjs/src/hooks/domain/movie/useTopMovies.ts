import { useQuery } from "@tanstack/react-query";
import { MovieAPI } from "@/services/api";

/**
 * Hook to fetch top-rated movies by IMDB rating
 *
 * @param year Optional year to filter movies by (defaults to current year if not provided)
 * @param isAllTime If true, fetches all-time top movies instead of year-specific
 * @param genreId Optional genre to filter by
 * @param limit Number of movies to return (default: 10)
 * @param page Page number for pagination (default: 1)
 * @param minVotes Minimum number of votes required (only used for all-time)
 * @returns Query result with top movies
 */
export const useTopMovies = (
  year?: number,
  isAllTime: boolean = false,
  genreId?: number,
  limit: number = 10,
  page: number = 1,
  minVotes: number = 100
) => {
  return useQuery({
    queryKey: ["top-movies", isAllTime, year, genreId, limit, page, minVotes],
    queryFn: () => {
      if (isAllTime) {
        return MovieAPI.getAllTimeTopMovies({
          page,
          limit,
          genre_id: genreId,
          min_votes: minVotes,
        });
      } else {
        return MovieAPI.getTopMovies({
          page,
          limit,
          year,
          genre_id: genreId,
        });
      }
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
  });
};

export default useTopMovies;
