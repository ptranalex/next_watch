import { Actor } from "@/domain/entities";
import { ComponentSize } from "../../ui/types";

/**
 * Actor Feature Types
 *
 * Types specific to actor components including detail views,
 * galleries, and actor cards.
 */

// ============================================================================
// Actor Component Props
// ============================================================================

/** Actor detail props */
export interface ActorDetailProps {
  actor: Actor;
  showMovies?: boolean;
  showBiography?: boolean;
}

/** Actor gallery props */
export interface ActorGalleryProps {
  movieId: number;
  maxActors?: number;
  showAllButton?: boolean;
}

/** Actor card props */
export interface ActorCardProps {
  actor: Actor;
  size?: ComponentSize;
  showRole?: boolean;
  onClick?: (actor: Actor) => void;
}
