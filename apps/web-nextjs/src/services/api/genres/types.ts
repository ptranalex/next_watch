/**
 * Types for Genre API
 */
import { Genre } from "../common/types";

export type { Genre };

export interface GenreResponse {
  genres: Genre[];
  total: number;
}
