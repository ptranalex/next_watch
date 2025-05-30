import { MovieAPI } from "@/services/api";
import { useQuery } from "@tanstack/react-query";
import { createLogger } from "@/utils/logging";
import { useEffect } from "react";

// Create logger for this hook
const logger = createLogger("useTopMovies");

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
  // Log hook initialization parameters
  logger.debug("useTopMovies initialized", {
    year,
    isAllTime,
    genreId,
    limit,
    page,
    minVotes,
  });

  const result = useQuery({
    queryKey: ["top-movies", isAllTime, year, genreId, limit, page, minVotes],
    queryFn: () => {
      if (isAllTime) {
        logger.info(
          `Fetching all-time top movies (page ${page}, limit ${limit})${
            genreId ? `, for genre ${genreId}` : ""
          }`
        );
        return MovieAPI.getAllTimeTopMovies({
          page,
          limit,
          genre_id: genreId,
          min_votes: minVotes,
        });
      } else {
        const yearValue = year || new Date().getFullYear();
        logger.info(
          `Fetching top movies for year ${yearValue} (page ${page}, limit ${limit})${
            genreId ? `, for genre ${genreId}` : ""
          }`
        );
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

  // Log results or errors
  useEffect(() => {
    if (result.error) {
      logger.error("Error fetching top movies:", result.error);
    } else if (result.data) {
      logger.info(
        `Fetched ${result.data.movies.length} top movies (total: ${
          result.data.total || "unknown"
        })`
      );
    }
  }, [result.data, result.error]);

  return result;
};

export default useTopMovies;
