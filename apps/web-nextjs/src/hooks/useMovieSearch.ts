import { useInfiniteQuery } from "@tanstack/react-query";
import { MovieAPI } from "../services/movies-api";

/**
 * Hook to search movies with infinite scrolling support
 *
 * @param query The search term
 * @param actorId Optional actor ID to filter results
 * @param genreId Optional genre ID to filter results
 * @returns InfiniteQuery result with movies matching the search criteria
 */
const useMovieSearch = (query: string, actorId?: number, genreId?: number) => {
  return useInfiniteQuery({
    queryKey: ["movie-search", query, actorId, genreId],
    queryFn: ({ pageParam = 1 }) =>
      MovieAPI.search(query, pageParam, actorId, genreId),
    getNextPageParam: (lastPage) => {
      // Check if there are more pages
      if (lastPage.page < Math.ceil(lastPage.total / lastPage.page_size)) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    enabled: query.length >= 2,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

export default useMovieSearch;
