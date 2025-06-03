import { Movie } from "@/domain/entities";
import type { MovieUpdateCallback } from "../types";

/** Movie detail page props */
export interface MovieDetailPageProps {
  /** Movie ID to display details for */
  movieId: number;
}

/** Movie detail view props */
export interface MovieDetailViewProps {
  movie: Movie;
  isSignedIn: boolean;
  onUpdateMovie?: MovieUpdateCallback;
  toggleFunctions?: {
    toggleWatched?: () => Promise<void>;
    toggleLiked?: () => Promise<void>;
    toggleWatchlist?: () => Promise<void>;
  };
  similarMovies?: Movie[];
}

/** Actor gallery props */
export interface ActorGalleryProps {
  movieId: number;
  castData?: {
    cast: Array<{
      id: number;
      name: string;
      actor_id: number;
      profile_path: string | null;
      character: string;
    }>;
  };
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
  trailers?: Array<{
    id: number;
    name: string;
    youtube_key: string;
    url_link: string;
    is_official: boolean;
    movie_id: number;
    created_at: string;
    updated_at: string;
  }>;
  isLoading?: boolean;
  error?: Error | null;
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
  size?: "sm" | "md" | "lg";
  orientation?: "vertical" | "horizontal";
  onUpdateMovie?: MovieUpdateCallback;
  toggleFunctions?: {
    toggleWatched?: () => Promise<void>;
    toggleLiked?: () => Promise<void>;
    toggleWatchlist?: () => Promise<void>;
  };
}
