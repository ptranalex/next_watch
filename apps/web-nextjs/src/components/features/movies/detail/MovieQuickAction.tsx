import ToggleIconButton from "@/components/ui/molecules/ToggleIconButton";
import CopyToClipboardButton from "@/components/features/movies/card/CopyToClipBoardButton";
import userInteractionAPI from "@/services/api/user/user-interaction-api";
import { HStack, useToast, VStack } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { HiBookmark, HiDocumentCheck, HiHeart } from "react-icons/hi2";
import { createLogger } from "@/utils/logging";
import type { MovieDetailQuickActionProps } from "./types";

// Create logger for this component
const logger = createLogger("MovieQuickAction");

const MovieQuickAction = ({
  movie,
  onUpdateMovie,
  size = "sm",
  orientation = "vertical",
}: MovieDetailQuickActionProps) => {
  const Stack = orientation === "vertical" ? VStack : HStack;
  const toast = useToast();
  const [isLoadingWatched, setIsLoadingWatched] = useState(false);
  const [isLoadingLiked, setIsLoadingLiked] = useState(false);
  const [isLoadingInWatchlist, setIsLoadingInWatchlist] = useState(false);

  // Log component initialization
  useEffect(() => {
    logger.debug(
      `MovieQuickAction initialized for: ${movie.title} (ID: ${movie.id})`
    );
    logger.debug(
      `Initial state: watched=${movie.watched}, liked=${movie.liked}, in_watchlist=${movie.in_watchlist}`
    );
  }, [movie.id, movie.title, movie.watched, movie.liked, movie.in_watchlist]);

  const handleWatched = async () => {
    if (isLoadingWatched) {
      logger.debug(`Watched toggle already in progress for movie ${movie.id}`);
      return;
    }

    const newValue = !movie.watched;
    logger.info(
      `Toggling watched status for ${movie.title} (${movie.id}): ${movie.watched} → ${newValue}`
    );
    setIsLoadingWatched(true);

    try {
      // Optimistic update
      const updatedMovie = { ...movie, watched: newValue };
      onUpdateMovie(updatedMovie);
      logger.debug(`Optimistic update applied for watched status: ${newValue}`);

      // API call
      logger.debug(`Calling toggleWatched API for movie ${movie.id}`);
      await userInteractionAPI.toggleWatched(movie.id as number);
      logger.info(
        `Successfully updated watched status on server for movie ${movie.id}`
      );

      // Success toast
      toast({
        title: `${newValue ? "Added to" : "Removed from"} watched`,
        description: `${movie.title} was ${
          newValue ? "marked as watched" : "unmarked as watched"
        }.`,
        status: "success",
        duration: 3000,
        isClosable: true,
        position: "bottom-right",
      });
    } catch (error) {
      // Error handling - revert optimistic update
      logger.error(
        `Failed to update watched status for movie ${movie.id}:`,
        error
      );
      const revertedMovie = { ...movie, watched: !newValue };
      onUpdateMovie(revertedMovie);
      logger.debug(
        `Optimistic update reverted for watched status to: ${!newValue}`
      );

      // Error toast
      toast({
        title: "Action Failed",
        description: `Failed to update watched status for ${movie.title}.`,
        status: "error",
        duration: 3000,
        isClosable: true,
        position: "bottom-right",
      });
    } finally {
      setIsLoadingWatched(false);
      logger.debug(`Watched toggle operation completed for movie ${movie.id}`);
    }
  };

  const handleLiked = async () => {
    if (isLoadingLiked) {
      logger.debug(`Liked toggle already in progress for movie ${movie.id}`);
      return;
    }

    const newValue = !movie.liked;
    logger.info(
      `Toggling liked status for ${movie.title} (${movie.id}): ${movie.liked} → ${newValue}`
    );
    setIsLoadingLiked(true);

    try {
      // Optimistic update
      const updatedMovie = { ...movie, liked: newValue };
      onUpdateMovie(updatedMovie);
      logger.debug(`Optimistic update applied for liked status: ${newValue}`);

      // API call
      logger.debug(`Calling toggleLiked API for movie ${movie.id}`);
      await userInteractionAPI.toggleLiked(movie.id as number);
      logger.info(
        `Successfully updated liked status on server for movie ${movie.id}`
      );

      // Success toast
      toast({
        title: `${newValue ? "Added to" : "Removed from"} liked`,
        description: `${movie.title} was ${
          newValue ? "added to" : "removed from"
        } your liked list.`,
        status: "success",
        duration: 3000,
        isClosable: true,
        position: "bottom-right",
      });
    } catch (error) {
      // Error handling - revert optimistic update
      logger.error(
        `Failed to update liked status for movie ${movie.id}:`,
        error
      );
      const revertedMovie = { ...movie, liked: !newValue };
      onUpdateMovie(revertedMovie);
      logger.debug(
        `Optimistic update reverted for liked status to: ${!newValue}`
      );

      // Error toast
      toast({
        title: "Action Failed",
        description: `Failed to update liked status for ${movie.title}.`,
        status: "error",
        duration: 3000,
        isClosable: true,
        position: "bottom-right",
      });
    } finally {
      setIsLoadingLiked(false);
      logger.debug(`Liked toggle operation completed for movie ${movie.id}`);
    }
  };

  const handleInWatchlist = async () => {
    if (isLoadingInWatchlist) {
      logger.debug(
        `Watchlist toggle already in progress for movie ${movie.id}`
      );
      return;
    }

    const newValue = !movie.in_watchlist;
    logger.info(
      `Toggling watchlist status for ${movie.title} (${movie.id}): ${movie.in_watchlist} → ${newValue}`
    );
    setIsLoadingInWatchlist(true);

    try {
      // Optimistic update
      const updatedMovie = { ...movie, in_watchlist: newValue };
      onUpdateMovie(updatedMovie);
      logger.debug(
        `Optimistic update applied for watchlist status: ${newValue}`
      );

      // API call
      logger.debug(`Calling toggleWatchlist API for movie ${movie.id}`);
      await userInteractionAPI.toggleWatchlist(movie.id as number);
      logger.info(
        `Successfully updated watchlist status on server for movie ${movie.id}`
      );

      // Success toast
      toast({
        title: `${newValue ? "Added to" : "Removed from"} watchlist`,
        description: `${movie.title} was ${
          newValue ? "added to" : "removed from"
        } your watch list.`,
        status: "success",
        duration: 3000,
        isClosable: true,
        position: "bottom-right",
      });
    } catch (error) {
      // Error handling - revert optimistic update
      logger.error(
        `Failed to update watchlist status for movie ${movie.id}:`,
        error
      );
      const revertedMovie = { ...movie, in_watchlist: !newValue };
      onUpdateMovie(revertedMovie);
      logger.debug(
        `Optimistic update reverted for watchlist status to: ${!newValue}`
      );

      // Error toast
      toast({
        title: "Action Failed",
        description: `Failed to update watchlist status for ${movie.title}.`,
        status: "error",
        duration: 3000,
        isClosable: true,
        position: "bottom-right",
      });
    } finally {
      setIsLoadingInWatchlist(false);
      logger.debug(
        `Watchlist toggle operation completed for movie ${movie.id}`
      );
    }
  };

  return (
    <Stack>
      <ToggleIconButton
        isActive={Boolean(movie.in_watchlist)}
        onToggle={handleInWatchlist}
        icon={<HiBookmark />}
        label="Add to Watch List"
        size={size}
        isLoading={isLoadingInWatchlist}
      />
      <ToggleIconButton
        isActive={Boolean(movie.liked)}
        onToggle={handleLiked}
        icon={<HiHeart />}
        label="Mark as liked"
        size={size}
        isLoading={isLoadingLiked}
      />
      <ToggleIconButton
        isActive={Boolean(movie.watched)}
        onToggle={handleWatched}
        icon={<HiDocumentCheck />}
        label="Mark as watched"
        size={size}
        isLoading={isLoadingWatched}
      />
      {movie.fshare_link && typeof movie.fshare_link === "string" && (
        <CopyToClipboardButton
          textToCopy={movie.fshare_link}
          label="Copy fshare link to clipboard"
          size={size}
        />
      )}
    </Stack>
  );
};

export default MovieQuickAction;
