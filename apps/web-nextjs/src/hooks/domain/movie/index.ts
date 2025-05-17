/**
 * Movie domain hooks
 * These hooks handle movie-related data and operations
 */

// Export all movie hooks
export { useMovies } from "./useMovies";
export { useMovie } from "./useMovie";
export { useMovieCast } from "./useMovieCast";
export { useMovieTrailer } from "./useMovieTrailer";
export { useTopMovies } from "./useTopMovies";

// Default export for backward compatibility
export { useMovies as default } from "./useMovies";
