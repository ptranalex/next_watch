/**
 * Types for Actor API
 */
import { Actor } from "../common/types";
import { MovieListResponse } from "../movies/types";

export type { Actor };

export interface ActorResponse {
  actors: Actor[];
  total: number;
  page?: number;
  page_size?: number;
}
