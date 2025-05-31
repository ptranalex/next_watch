import { bffFetchData } from "../core/api-client";
import {
  BFFMovieListResponse,
  BFFMovieQueryParams,
  MovieDetailData,
  HomeScreenData,
  GenreScreenData,
  SearchResults,
} from "./types";
import { createLogger } from "@/utils/logging";

const logger = createLogger("BFFMoviesAPI");

/**
 * BFF Movies API - All movie-related operations through the BFF layer
 * This provides better performance, caching, and user experience optimization
 */
export const BFFMoviesAPI = {
  /**
   * Get movies with comprehensive filtering and pagination
   */
  getMovies: async (
    params: BFFMovieQueryParams = {}
  ): Promise<BFFMovieListResponse> => {
    const queryParams = new URLSearchParams();

    if (params.page) queryParams.append("page", params.page.toString());
    if (params.limit) queryParams.append("limit", params.limit.toString());
    if (params.genre_id)
      queryParams.append("genre_id", params.genre_id.toString());
    if (params.actor_id)
      queryParams.append("actor_id", params.actor_id.toString());
    if (params.sort_by) queryParams.append("sort_by", params.sort_by);
    if (params.sort_desc !== undefined)
      queryParams.append("sort_desc", params.sort_desc.toString());
    if (params.imdb_rating)
      queryParams.append("imdb_rating", params.imdb_rating.toString());
    if (params.rotten_tomatoes_rating)
      queryParams.append(
        "rotten_tomatoes_rating",
        params.rotten_tomatoes_rating.toString()
      );
    if (params.metacritic_rating)
      queryParams.append(
        "metacritic_rating",
        params.metacritic_rating.toString()
      );
    if (params.year) queryParams.append("year", params.year.toString());
    if (params.start_year)
      queryParams.append("start_year", params.start_year.toString());
    if (params.end_year)
      queryParams.append("end_year", params.end_year.toString());

    const endpoint = `/bff/v1/movies${
      queryParams.toString() ? `?${queryParams.toString()}` : ""
    }`;

    logger.debug("Fetching movies with params:", params);
    return bffFetchData<BFFMovieListResponse>(endpoint);
  },

  /**
   * Get detailed movie information including cast, trailers, and user interactions
   */
  getMovieDetail: async (movieId: number): Promise<MovieDetailData> => {
    logger.debug("Fetching movie detail:", { movieId });
    return bffFetchData<MovieDetailData>(`/bff/v1/movies/${movieId}`);
  },

  /**
   * Get aggregated home screen data
   */
  getHomeScreen: async (userId?: number): Promise<HomeScreenData> => {
    const endpoint = userId ? `/bff/v1/home?user_id=${userId}` : "/bff/v1/home";

    logger.debug("Fetching home screen data:", { userId });
    return bffFetchData<HomeScreenData>(endpoint);
  },

  /**
   * Get movies by genre with pagination
   */
  getMoviesByGenre: async (
    genreId: number,
    params: Omit<BFFMovieQueryParams, "genre_id"> = {}
  ): Promise<GenreScreenData> => {
    const queryParams = new URLSearchParams();

    if (params.page) queryParams.append("page", params.page.toString());
    if (params.limit) queryParams.append("limit", params.limit.toString());
    if (params.sort_by) queryParams.append("sort", params.sort_by);
    if (params.sort_desc !== undefined)
      queryParams.append("sort_desc", params.sort_desc.toString());

    const endpoint = `/bff/v1/genres/${genreId}${
      queryParams.toString() ? `?${queryParams.toString()}` : ""
    }`;

    logger.debug("Fetching movies by genre:", { genreId, params });
    return bffFetchData<GenreScreenData>(endpoint);
  },

  /**
   * Search movies
   */
  searchMovies: async (
    query: string,
    params: Omit<BFFMovieQueryParams, "search"> = {}
  ): Promise<SearchResults> => {
    const queryParams = new URLSearchParams();
    queryParams.append("q", query);

    if (params.page) queryParams.append("page", params.page.toString());
    if (params.limit) queryParams.append("limit", params.limit.toString());

    const endpoint = `/bff/v1/search?${queryParams.toString()}`;

    logger.debug("Searching movies:", { query, params });
    return bffFetchData<SearchResults>(endpoint);
  },

  /**
   * Get top movies (could be implemented as a filter on getMovies)
   */
  getTopMovies: async (
    params: {
      page?: number;
      limit?: number;
      year?: number;
      genre_id?: number;
    } = {}
  ): Promise<BFFMovieListResponse> => {
    // Use the main getMovies endpoint with sorting by rating
    return BFFMoviesAPI.getMovies({
      ...params,
      sort_by: "imdb_rating",
      sort_desc: true,
      imdb_rating: 7.0, // Only get well-rated movies
    });
  },

  /**
   * Get movies by actor
   */
  getMoviesByActor: async (
    actorId: number,
    params: Omit<BFFMovieQueryParams, "actor_id"> = {}
  ): Promise<BFFMovieListResponse> => {
    return BFFMoviesAPI.getMovies({
      ...params,
      actor_id: actorId,
    });
  },

  /**
   * Get recent releases
   */
  getRecentReleases: async (
    params: {
      page?: number;
      limit?: number;
    } = {}
  ): Promise<BFFMovieListResponse> => {
    const currentYear = new Date().getFullYear();
    return BFFMoviesAPI.getMovies({
      ...params,
      start_year: currentYear - 1, // Last year to current
      sort_by: "release_date",
      sort_desc: true,
    });
  },

  /**
   * Get popular movies
   */
  getPopularMovies: async (
    params: {
      page?: number;
      limit?: number;
    } = {}
  ): Promise<BFFMovieListResponse> => {
    return BFFMoviesAPI.getMovies({
      ...params,
      sort_by: "imdb_rating", // Assuming popularity correlates with rating
      sort_desc: true,
      imdb_rating: 6.0, // Minimum quality threshold
    });
  },
};
