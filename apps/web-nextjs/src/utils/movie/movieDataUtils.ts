import { Genre, Movie } from "@/domain/entities";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("movieDataUtils");

/**
 * Utilities for safe movie data access with proper type checking
 */
export const movieUtils = {
  /**
   * Safely extracts the movie ID as a number
   */
  getMovieId: (movie: Movie): number => {
    return typeof movie.id === "number" ? movie.id : 0;
  },

  /**
   * Extracts release year from date string
   */
  getReleaseYear: (movie: Movie): string => {
    if (!movie.release_date) return "";
    try {
      return new Date(movie.release_date.toString()).getFullYear().toString();
    } catch (e) {
      logger.warn(`Failed to parse release date: ${movie.release_date}`, e);
      return "";
    }
  },

  /**
   * Safely renders any value as a string
   */
  renderText: (value: unknown): string => {
    if (value === undefined || value === null) return "";
    return String(value);
  },

  /**
   * Formats movie genres as a comma-separated string
   */
  renderGenres: (movie: Movie): string => {
    if (!movie.genres || !Array.isArray(movie.genres)) {
      logger.debug(`Movie ${movie.id} has no genres`);
      return "N/A";
    }
    return (
      movie.genres
        .filter(
          (genre): genre is Genre =>
            typeof genre === "object" && genre !== null && "name" in genre
        )
        .map((genre) => genre.name)
        .join(", ") || "N/A"
    );
  },

  /**
   * Extracts rating data in a consistent format
   */
  extractRatings: (movie: Movie) => {
    return {
      imdb_rating:
        typeof movie.imdb_rating === "number" ? movie.imdb_rating : null,
      rotten_tomatoes_rating:
        typeof movie.rotten_tomatoes_rating === "number"
          ? movie.rotten_tomatoes_rating
          : null,
      metacritic_rating:
        typeof movie.metacritic_rating === "number"
          ? movie.metacritic_rating
          : null,
    };
  },
};
