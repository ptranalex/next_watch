import { Movie } from "@/domain/entities";
import type { MovieUpdateCallback } from "../types";

export interface MovieDetailViewProps {
  movie: Movie;
  isSignedIn: boolean;
  onUpdateMovie: MovieUpdateCallback;
}

export interface MovieRatings {
  imdb_rating: number | null;
  rotten_tomatoes_rating: number | null;
  metacritic_rating: number | null;
}

/** Rating group component props */
export interface RatingGroupProps {
  movie: MovieRatings;
  scale_up?: number;
}

/** Trailer card component props */
export interface TrailerCardProps {
  movieId: number;
}

/** Critic score component props */
export interface CriticScoreProps {
  source: string;
  value: number | null | undefined;
  scale_up?: number;
}

/** Movie attributes component props */
export interface MovieAttributesProps {
  movie: Movie;
}

/** Movie skeleton component props */
export interface MovieSkeletonProps {
  isSmallerScreen?: boolean;
}

/** Movie error state props */
export interface MovieErrorStateProps {
  error?: Error | string;
}

/** Movie not found state props */
export interface MovieNotFoundStateProps {
  message?: string;
}

/** Movie detail quick action props - specific to detail view usage */
export interface MovieDetailQuickActionProps {
  movie: Movie;
  onUpdateMovie: MovieUpdateCallback;
  size?: "sm" | "md" | "lg";
  orientation?: "vertical" | "horizontal";
}
