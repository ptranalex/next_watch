import type { Movie } from "./movies/Movie.entity";
import type { Actor } from "./actors/Actor.entity";
import type { Genre } from "./genres/Genre.entity";

/**
 * Type guard to check if an object is a valid Movie entity
 */
export function isMovie(obj: any): obj is Movie {
  return (
    typeof obj === "object" &&
    obj !== null &&
    typeof obj.id === "number" &&
    typeof obj.title === "string"
  );
}

/**
 * Type guard to check if an object is a valid Actor entity
 */
export function isActor(obj: any): obj is Actor {
  return (
    typeof obj === "object" &&
    obj !== null &&
    typeof obj.id === "number" &&
    typeof obj.name === "string" &&
    obj.actor_id !== undefined
  );
}

/**
 * Type guard to check if an object is a valid Genre entity
 */
export function isGenre(obj: any): obj is Genre {
  return (
    typeof obj === "object" &&
    obj !== null &&
    typeof obj.id === "number" &&
    typeof obj.name === "string" &&
    !("actor_id" in obj) // distinguish from Actor
  );
}
