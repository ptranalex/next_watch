import { useQuery } from "@tanstack/react-query";
import { fetchData } from "../services/api-client";
import { MovieListResponse } from "../services/movie-service";

/**
 * Hook to fetch top-rated movies by IMDB rating
 *
 * @param year Optional year to filter movies by (defaults to current year if not provided)
 * @param isAllTime If true, fetches all-time top movies instead of year-specific
 * @param genre Optional genre to filter by
 * @param limit Number of movies to return (default: 10)
 * @param page Page number for pagination (default: 1)
 * @param minVotes Minimum number of votes required (only used for all-time)
 * @returns Query result with top movies
 */
export const useTopMovies = (
  year?: number,
  isAllTime: boolean = false,
  genre?: string,
  limit: number = 10,
  page: number = 1,
  minVotes: number = 100
) => {
  // Determine the base endpoint
  const endpoint = isAllTime ? "/movies/top/all-time" : "/movies/top";

  // Build query parameters
  const params = new URLSearchParams();

  if (!isAllTime && year) {
    params.append("year", year.toString());
  }

  if (genre) {
    params.append("genre", genre);
  }

  if (isAllTime && minVotes > 0) {
    params.append("min_votes", minVotes.toString());
  }

  params.append("limit", limit.toString());
  params.append("page", page.toString());

  // Construct full URL
  const url = `${endpoint}?${params.toString()}`;

  return useQuery<MovieListResponse>({
    queryKey: ["top-movies", isAllTime, year, genre, limit, page, minVotes],
    queryFn: () => fetchData(url),
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
  });
};

export default useTopMovies;
