/**
 * Entity Types
 *
 * This module provides UI-friendly entity types that extend the service API types.
 * It includes conversion utilities to transform between service and UI representations.
 */

// Movie exports
export type { Movie } from "./movies";
export { toMovieEntity, toServiceMovie } from "./movies";

// Actor exports
export type { Actor } from "./actors";
export { toActorEntity, toServiceActor } from "./actors";

// Genre exports
export type { Genre } from "./genres";
export { toGenreEntity, toServiceGenre } from "./genres";

// Type guards
export { isMovie, isActor, isGenre } from "./type-guards";
