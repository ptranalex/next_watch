/**
 * Types for Genre API
 */
import { Genre } from "../common/types";
import { GenreScreenData } from "../bff/types";

export type { Genre, GenreScreenData };

export interface GenreResponse {
  genres: Genre[];
  total: number;
}
