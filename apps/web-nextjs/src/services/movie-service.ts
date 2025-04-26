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

export interface Actor {
  id: number; // Credit ID in some contexts, but generally actor_id/tmdb_person_id will be used as the primary identifier
  actor_id: number; // TMDB person ID - primary identifier across the app
  name: string;
  profile_path?: string;
  biography?: string;
  birthday?: string;
  place_of_birth?: string;
  popularity?: number;
  gender?: number;
  known_for_department?: string;
  also_known_as?: string[];
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
 * Streaming source interface representing a video source for a movie
 */
export interface StreamingSource {
  id: string;
  title: string;
  quality: string;
  url: string;
  provider: string;
  type: "trailer" | "full" | "clip";
}

/**
 * Movie streaming sources response
 */
export interface MovieStreamingResponse {
  movie_id: number;
  title: string;
  sources: StreamingSource[];
}

/**
 * Movie cast response
 */
export interface MovieCastResponse {
  cast: {
    id: number;
    actor_id: number;
    name: string;
    character?: string;
    profile_path?: string;
    order?: number;
  }[];
  movie_id: number;
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
 * Fetch actor details by actor ID (which is the TMDB person ID)
 */
export const getActorById = async (actorId: number): Promise<Actor> => {
  try {
    // First try to get movies featuring this actor using actor_id (TMDB person ID)
    const moviesResponse = await fetchData<MovieListResponse>(
      `/movies?actor_id=${actorId}&limit=1`
    );

    if (moviesResponse.movies.length === 0) {
      throw new Error(`No movies found for actor with ID ${actorId}`);
    }

    // Get the first movie to extract cast information
    const movie = moviesResponse.movies[0];
    const castResponse = await fetchData<any>(`/movies/${movie.id}/cast`);

    // Find the actor in the cast (matching by actor_id)
    const actorInfo = castResponse.cast.find(
      (member: any) => member.actor_id === actorId
    );

    if (!actorInfo) {
      throw new Error(`Actor with ID ${actorId} not found in cast`);
    }

    // Return formatted actor info
    return {
      id: actorInfo.id, // Credit ID
      actor_id: actorInfo.actor_id, // TMDB person ID
      name: actorInfo.name,
      profile_path: actorInfo.profile_path,
      // Other fields will be undefined until we get more data
    };
  } catch (error) {
    console.error(`Error fetching actor ${actorId}:`, error);
    throw error;
  }
};

/**
 * Fetch movies featuring a specific actor by internal ID
 */
export const getMoviesByActor = async (
  actorId: number,
  page: number = 1,
  limit: number = 20
): Promise<MovieListResponse> => {
  // Use the movies endpoint with actor filter (using internal actor ID)
  const queryParams = new URLSearchParams();
  queryParams.append("actor_id", actorId.toString());
  queryParams.append("page", page.toString());
  queryParams.append("limit", limit.toString());

  try {
    return await fetchData<MovieListResponse>(
      `/movies?${queryParams.toString()}`
    );
  } catch (error) {
    console.error(`Error fetching movies for actor ${actorId}:`, error);
    // Return empty results on error
    return {
      movies: [],
      total: 0,
      page: page,
      page_size: limit,
    };
  }
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

/**
 * Fetch popular actors
 */
export const getPopularActors = async (
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
};

/**
 * Fetch streaming sources for a movie
 */
export const getMovieStreamingSources = async (
  movieId: number
): Promise<MovieStreamingResponse> => {
  return fetchData<MovieStreamingResponse>(`/movies/${movieId}/watch`);
};
