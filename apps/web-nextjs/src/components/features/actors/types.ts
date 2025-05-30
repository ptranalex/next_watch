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

/** Actor page props */
export interface ActorPageProps {
  /** Actor ID to display movies for */
  actorId: number;
}

/** Actor detail props */
export interface ActorDetailProps {
  actor: Actor;
  showMovies?: boolean;
  showBiography?: boolean;
}

/** Cast member type for the ActorGallery component */
export interface CastMember {
  id: number;
  name: string;
  actor_id: number;
  profile_path?: string;
  character?: string;
}

/** Cast data type for the ActorGallery component */
export interface CastData {
  cast: CastMember[];
}

/** Actor gallery props */
export interface ActorGalleryProps {
  movieId: number;
  castData: CastData;
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
