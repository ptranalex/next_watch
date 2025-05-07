import { APIClient, fetchData } from "../core/api-client";
import {
  Movie,
  MovieListResponse,
  MoviesQueryParams,
  MovieStreamingResponse,
  MovieCastResponse,
} from "./types";
import { Genre } from "../common/types";

/**
 * Client for movie-related API operations
 */
export const moviesClient = new APIClient<Movie>("/api/v1/movies");

/**
 * Enhanced Movie API with specialized methods beyond basic CRUD
 */
export const MovieAPI = {
  /**
   * Get movies with pagination and filters
   */
  getMovies: async (params: MoviesQueryParams): Promise<MovieListResponse> => {
    const queryParams = new URLSearchParams();

    if (params.page) queryParams.append("page", params.page.toString());
    if (params.pageSize)
      queryParams.append("limit", params.pageSize.toString());
    if (params.genre_id)
      queryParams.append("genre_id", params.genre_id.toString());
    if (params.actor_id)
      queryParams.append("actor_id", params.actor_id.toString());
    if (params.search) queryParams.append("search", params.search);

    // Map frontend sort names to backend field names
    const sortMapping: Record<string, string> = {
      released: "release_date",
      // Add other mappings if needed
    };

    // Use the mapping if it exists, otherwise use the provided sortBy value
    if (params.sortBy) {
      const backendSortField = sortMapping[params.sortBy] || params.sortBy;
      queryParams.append("sort_by", backendSortField);
    }

    // Always add sort_desc parameter for clarity
    queryParams.append("sort_desc", (params.sort_desc === true).toString());

    // Add rating filter parameters
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

    return fetchData<MovieListResponse>(
      `/api/v1/movies?${queryParams.toString()}`
    );
  },

  /**
   * Get a single movie by ID
   */
  getById: async (id: number): Promise<Movie> => {
    return moviesClient.getById(id);
  },

  /**
   * Get movies by genre ID
   */
  getMoviesByGenre: async (
    genreId: number,
    params: Omit<MoviesQueryParams, "genre_id"> = {}
  ): Promise<MovieListResponse> => {
    return MovieAPI.getMovies({ ...params, genre_id: genreId });
  },

  /**
   * Get movies by actor ID
   */
  getMoviesByActor: async (
    actorId: number,
    params: Omit<MoviesQueryParams, "actor_id"> = {}
  ): Promise<MovieListResponse> => {
    return MovieAPI.getMovies({ ...params, actor_id: actorId });
  },

  /**
   * Search movies by title or content
   */
  search: async (
    query: string,
    params: Omit<MoviesQueryParams, "search"> = {}
  ): Promise<MovieListResponse> => {
    return MovieAPI.getMovies({ ...params, search: query });
  },

  /**
   * Get top rated movies
   */
  getTopMovies: async (params: {
    page?: number;
    limit?: number;
    year?: number;
    genre_id?: number;
  }): Promise<MovieListResponse> => {
    const queryParams = new URLSearchParams();

    if (params.page) queryParams.append("page", params.page.toString());
    if (params.limit) queryParams.append("limit", params.limit.toString());
    if (params.year) queryParams.append("year", params.year.toString());
    if (params.genre_id)
      queryParams.append("genre_id", params.genre_id.toString());

    return fetchData<MovieListResponse>(
      `/api/v1/movies/top?${queryParams.toString()}`
    );
  },

  /**
   * Get all-time top rated movies
   */
  getAllTimeTopMovies: async (params: {
    page?: number;
    limit?: number;
    genre_id?: number;
    min_votes?: number;
  }): Promise<MovieListResponse> => {
    const queryParams = new URLSearchParams();

    if (params.page) queryParams.append("page", params.page.toString());
    if (params.limit) queryParams.append("limit", params.limit.toString());
    if (params.genre_id)
      queryParams.append("genre_id", params.genre_id.toString());
    if (params.min_votes)
      queryParams.append("min_votes", params.min_votes.toString());

    return fetchData<MovieListResponse>(
      `/api/v1/movies/top/all-time?${queryParams.toString()}`
    );
  },

  /**
   * Get streaming sources for a movie
   */
  getStreamingSources: async (
    movieId: number
  ): Promise<MovieStreamingResponse> => {
    return fetchData<MovieStreamingResponse>(
      `/api/v1/movies/${movieId}/sources`
    );
  },

  /**
   * Get cast for a movie
   */
  getCast: async (movieId: number): Promise<MovieCastResponse> => {
    return fetchData<MovieCastResponse>(`/api/v1/movies/${movieId}/cast`);
  },

  /**
   * Rate a movie
   */
  rateMovie: async (
    movieId: number,
    rating: number
  ): Promise<{ success: boolean }> => {
    return moviesClient.query(`${movieId}/rate`, {
      method: "POST",
      data: { rating },
    });
  },

  /**
   * Get all movie genres
   */
  getAllGenres: async (): Promise<Genre[]> => {
    const response = await fetchData<{ genres: Genre[]; total: number }>(
      "/api/v1/genres"
    );
    return response.genres;
  },

  /**
   * Get related movies for a movie
   */
  getRelatedMovies: async (movieId: number): Promise<MovieListResponse> => {
    return fetchData<MovieListResponse>(`/api/v1/movies/${movieId}/related`);
  },
};
