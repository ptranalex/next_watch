import { APIClient, fetchData } from "./api-client";
import {
  Movie,
  MovieListResponse,
  Genre,
  Actor,
  MovieCastResponse,
  MovieStreamingResponse,
} from "./movie-service";

// Types for search suggestions
export interface Suggestion {
  type: "movie" | "actor" | "genre";
  info: Movie | Actor | Genre;
}

export interface SuggestionsResponse {
  suggestions: Suggestion[];
}

/**
 * Client for movie-related API operations
 */
export const moviesClient = new APIClient<Movie>("/movies");

/**
 * Enhanced Movie API with specialized methods beyond basic CRUD
 */
export const MovieAPI = {
  /**
   * Get movies with pagination and filters
   */
  getMovies: async (params: {
    page?: number;
    limit?: number;
    genre_id?: number;
    actor_id?: number;
    sort_by?: string;
    sort_desc?: boolean;
  }): Promise<MovieListResponse> => {
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

    return fetchData<MovieListResponse>(`/movies?${queryParams.toString()}`);
  },

  /**
   * Get a movie by ID
   */
  getById: async (id: number): Promise<Movie> => {
    return moviesClient.getById(id);
  },

  /**
   * Search for movies
   */
  search: async (
    query: string,
    page: number = 1,
    actorId?: number,
    genreId?: number
  ): Promise<MovieListResponse> => {
    const queryParams = new URLSearchParams();
    queryParams.append("query", query);
    queryParams.append("page", page.toString());

    if (actorId) queryParams.append("actor_id", actorId.toString());
    if (genreId) queryParams.append("genre_id", genreId.toString());

    return fetchData<MovieListResponse>(
      `/movies/search?${queryParams.toString()}`
    );
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
      `/movies/top?${queryParams.toString()}`
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
      `/movies/top/all-time?${queryParams.toString()}`
    );
  },

  /**
   * Get cast for a movie
   */
  getCast: async (movieId: number): Promise<MovieCastResponse> => {
    return moviesClient.query<MovieCastResponse>(`${movieId}/cast`);
  },

  /**
   * Get streaming sources for a movie
   */
  getStreamingSources: async (
    movieId: number
  ): Promise<MovieStreamingResponse> => {
    return moviesClient.query<MovieStreamingResponse>(`${movieId}/watch`);
  },

  /**
   * Get related movies for a movie
   */
  getRelatedMovies: async (movieId: number): Promise<MovieListResponse> => {
    return fetchData<MovieListResponse>(`/movies/${movieId}/related`);
  },
};

/**
 * Client for genre-related API operations
 */
export const genresClient = new APIClient<Genre>("/genres");

/**
 * Enhanced Genre API
 */
export const GenreAPI = {
  /**
   * Get all genres
   */
  getAll: async (): Promise<Genre[]> => {
    const response = await fetchData<{ genres: Genre[]; total: number }>(
      "/genres/"
    );
    return response.genres;
  },

  /**
   * Get a genre by ID
   */
  getById: async (id: number): Promise<Genre | undefined> => {
    const genres = await GenreAPI.getAll();
    return genres.find((genre) => genre.id === id);
  },
};

/**
 * Client for actor-related API operations
 */
export const actorsClient = new APIClient<Actor>("/actors");

/**
 * Enhanced Actor API
 */
export const ActorAPI = {
  /**
   * Get popular actors
   */
  getPopular: async (
    page: number = 1,
    limit: number = 20
  ): Promise<{
    actors: Actor[];
    total: number;
    page: number;
    page_size: number;
  }> => {
    const queryParams = new URLSearchParams();
    queryParams.append("page", page.toString());
    queryParams.append("limit", limit.toString());

    return fetchData<{
      actors: Actor[];
      total: number;
      page: number;
      page_size: number;
    }>(`/actors/popular?${queryParams.toString()}`);
  },

  /**
   * Get an actor by ID
   */
  getById: async (actorId: number): Promise<Actor> => {
    return actorsClient.getById(actorId);
  },

  /**
   * Get movies featuring an actor
   */
  getMovies: async (
    actorId: number,
    page: number = 1,
    limit: number = 20
  ): Promise<MovieListResponse> => {
    const queryParams = new URLSearchParams();
    queryParams.append("actor_id", actorId.toString());
    queryParams.append("page", page.toString());
    queryParams.append("limit", limit.toString());

    return fetchData<MovieListResponse>(`/movies?${queryParams.toString()}`);
  },
};

/**
 * Enhanced Search API
 */
export const SearchAPI = {
  /**
   * Get search suggestions
   */
  getSuggestions: async (query: string): Promise<Suggestion[]> => {
    if (!query || query.length < 2) return [];

    const data = await fetchData<SuggestionsResponse>(
      `/search/suggestions?q=${encodeURIComponent(query)}`
    );

    return data.suggestions;
  },
};
