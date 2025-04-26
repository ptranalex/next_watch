import { fetchData } from "./api-client";

// Types
export interface Movie {
  id: number;
  title: string;
  overview?: string;
  poster_path?: string;
  backdrop_path?: string;
  poster_url?: string;
  backdrop_url?: string;
  vote_average?: number;
  release_date?: string;
  genres?: Genre[];
}

export interface Genre {
  id: number;
  name: string;
}

export interface MovieListResponse {
  movies: Movie[];
  total: number;
  page: number;
  page_size: number;
}

export interface MoviesQueryParams {
  page?: number;
  pageSize?: number;
  genre_id?: number;
  actor_id?: number;
  search?: string;
  sortBy?: string;
}

/**
 * Fetch a list of movies with optional filtering and pagination
 */
export const getMovies = async (
  params: MoviesQueryParams = {}
): Promise<MovieListResponse> => {
  const queryParams = new URLSearchParams();

  if (params.page) queryParams.append("page", params.page.toString());
  if (params.pageSize)
    queryParams.append("pageSize", params.pageSize.toString());
  if (params.genre_id)
    queryParams.append("genre_id", params.genre_id.toString());
  if (params.actor_id)
    queryParams.append("actor_id", params.actor_id.toString());
  if (params.search) queryParams.append("search", params.search);
  if (params.sortBy) queryParams.append("sortBy", params.sortBy);

  const endpoint = `/movies?${queryParams.toString()}`;

  return fetchData<MovieListResponse>(endpoint);
};

/**
 * Fetch a single movie by ID
 */
export const getMovieById = async (id: number): Promise<Movie> => {
  return fetchData<Movie>(`/movies/${id}`);
};

/**
 * Fetch a list of genres
 */
export const getGenres = async (): Promise<Genre[]> => {
  const response = await fetchData<{ genres: Genre[]; total: number }>(
    "/genres/"
  );
  return response.genres;
};

/**
 * Fetch movies by genre
 */
export const getMoviesByGenre = async (
  genreId: number,
  page: number = 1,
  limit: number = 20,
  actorId?: number
): Promise<MovieListResponse> => {
  // Use the movies endpoint with genre filter
  const queryParams = new URLSearchParams();
  queryParams.append("genre_id", genreId.toString());
  queryParams.append("page", page.toString());
  queryParams.append("limit", limit.toString());

  if (actorId) {
    queryParams.append("actor_id", actorId.toString());
  }

  return fetchData<MovieListResponse>(`/movies?${queryParams.toString()}`);
};

/**
 * Search for movies
 */
export const searchMovies = async (
  query: string,
  page: number = 1,
  actorId?: number,
  genreId?: number
): Promise<MovieListResponse> => {
  const queryParams = new URLSearchParams();
  queryParams.append("query", query);
  queryParams.append("page", page.toString());

  if (actorId) {
    queryParams.append("actor_id", actorId.toString());
  }

  if (genreId) {
    queryParams.append("genre_id", genreId.toString());
  }

  return fetchData<MovieListResponse>(
    `/movies/search?${queryParams.toString()}`
  );
};

/**
 * Fetch movies featuring a specific actor by TMDB person ID
 */
export const getMoviesByActor = async (
  actorId: number,
  page: number = 1,
  limit: number = 20
): Promise<MovieListResponse> => {
  // Use the movies endpoint with actor filter
  const queryParams = new URLSearchParams();
  queryParams.append("actor_id", actorId.toString());
  queryParams.append("page", page.toString());
  queryParams.append("limit", limit.toString());

  return fetchData<MovieListResponse>(`/movies?${queryParams.toString()}`);
};

/**
 * Fetch top rated movies with optional filters
 */
export const getTopMovies = async (
  page: number = 1,
  limit: number = 20,
  year?: number,
  genreId?: number
): Promise<MovieListResponse> => {
  const queryParams = new URLSearchParams();
  queryParams.append("page", page.toString());
  queryParams.append("limit", limit.toString());

  if (year) {
    queryParams.append("year", year.toString());
  }

  if (genreId) {
    queryParams.append("genre_id", genreId.toString());
  }

  return fetchData<MovieListResponse>(`/movies/top?${queryParams.toString()}`);
};

/**
 * Get a genre by its ID
 */
export const getGenreById = async (id: number): Promise<Genre | undefined> => {
  const genres = await getGenres();
  return genres.find((genre) => genre.id === id);
};
