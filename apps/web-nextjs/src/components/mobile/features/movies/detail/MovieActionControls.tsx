import React from "react";
import { ActionPill } from "@/components/mobile/ui/action-pill";
import type { ActionPillItem } from "@/components/mobile/ui/action-pill";
import { Movie } from "@/domain/entities";
import { createLogger } from "@/utils/logging";
import {
  HiCheck,
  HiOutlineCheck,
  HiHeart,
  HiOutlineHeart,
  HiBookmark,
  HiOutlineBookmark,
} from "react-icons/hi";

// Create logger for this component
const logger = createLogger("MovieActionControls");

interface MovieActionControlsProps {
  movie: Movie;
  onUpdateMovie: (movie: Movie) => void;
  disabled?: boolean;
}

/**
 * MovieActionControls component
 * Encapsulates the movie action controls using the generic ActionPill
 * Focuses on state management (active/disabled) rather than UI details
 */
const MovieActionControls: React.FC<MovieActionControlsProps> = ({
  movie,
  onUpdateMovie,
  disabled = false,
}) => {
  // Action handlers
  const handleWatchedToggle = () => {
    logger.info(`Toggle watched state for movie: ${movie.id}`);
    onUpdateMovie({ ...movie, watched: !movie.watched });
  };

  const handleLikedToggle = () => {
    logger.info(`Toggle liked state for movie: ${movie.id}`);
    onUpdateMovie({ ...movie, liked: !movie.liked });
  };

  const handleWatchlistToggle = () => {
    logger.info(`Toggle watchlist state for movie: ${movie.id}`);
    onUpdateMovie({ ...movie, in_watchlist: !movie.in_watchlist });
  };

  // Create movie actions for ActionPill - focus on state, not UI details
  const movieActions: ActionPillItem[] = [
    {
      id: "watched",
      label: movie.watched ? "Watched" : "Watch",
      icon: movie.watched ? <HiCheck /> : <HiOutlineCheck />,
      onClick: handleWatchedToggle,
      disabled: disabled,
      active: movie.watched,
      activeColor: "colors.primary", // Using semantic token
    },
    {
      id: "favorite",
      label: movie.liked ? "Favorited" : "Favorite",
      icon: movie.liked ? <HiHeart /> : <HiOutlineHeart />,
      onClick: handleLikedToggle,
      disabled: disabled,
      active: movie.liked,
      activeColor: "feedback.success", // Using semantic token
    },
    {
      id: "watchlist",
      label: "Watchlist",
      icon: movie.in_watchlist ? <HiBookmark /> : <HiOutlineBookmark />,
      onClick: handleWatchlistToggle,
      disabled: disabled,
      active: movie.in_watchlist,
      activeColor: "colors.secondary", // Using semantic token
    },
  ];

  return <ActionPill actions={movieActions} />;
};

export default MovieActionControls;
