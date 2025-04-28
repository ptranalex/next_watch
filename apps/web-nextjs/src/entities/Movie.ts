import { Genre } from "../services/movie-service";

/**
 * Movie entity with additional fields for user actions like watch list, liked, etc.
 */
interface Movie {
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

  // User-specific fields
  is_watched?: boolean;
  is_liked?: boolean;
  to_watch?: boolean;

  // Additional fields from the React JS reference
  imdb_id?: string;
  rating_imdb?: number;
  fshare_link?: string;

  // Index signature to allow attribute access by string
  [key: string]: any;
}

export default Movie;
