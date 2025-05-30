import { Genre } from "@/domain/entities";
import { ComponentSize } from "../../ui/types";

/**
 * Genre Feature Types
 *
 * Types specific to genre components including detail views,
 * galleries, and genre cards.
 */

// ============================================================================
// Genre Component Props
// ============================================================================

/** Genre page props */
export interface GenrePageProps {
  /** Genre ID to display movies for */
  genreId: number;
}

/** Genre detail props */
export interface GenreDetailProps {
  genre: Genre;
  showMovies?: boolean;
  showDescription?: boolean;
}

/** Genre card props */
export interface GenreCardProps {
  genre: Genre;
  size?: ComponentSize;
  showMovieCount?: boolean;
  onClick?: (genre: Genre) => void;
}

/** Genre gallery props */
export interface GenreGalleryProps {
  genres: Genre[];
  maxGenres?: number;
  showAllButton?: boolean;
  onGenreClick?: (genre: Genre) => void;
}
