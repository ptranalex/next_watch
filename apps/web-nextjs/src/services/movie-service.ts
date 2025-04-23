import { fetchData } from "./api-client";

// Types
export interface Movie {
  id: number;
  title: string;
  overview?: string;
  poster_path?: string;
  backdrop_path?: string;
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
  genre?: string;
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
  if (params.genre) queryParams.append("genre", params.genre);
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
    "/genres"
  );
  return response.genres;
};

/**
 * Fetch movies by genre
 */
export const getMoviesByGenre = async (
  genreName: string,
  page: number = 1
): Promise<MovieListResponse> => {
  return fetchData<MovieListResponse>(`/genre/${genreName}?page=${page}`);
};

/**
 * Search for movies
 */
export const searchMovies = async (
  query: string,
  page: number = 1
): Promise<MovieListResponse> => {
  return fetchData<MovieListResponse>(
    `/movies/search?query=${encodeURIComponent(query)}&page=${page}`
  );
};
