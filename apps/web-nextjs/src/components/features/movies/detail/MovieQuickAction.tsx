import ToggleIconButton from "@/components/ui/molecules/ToggleIconButton";
import CopyToClipboardButton from "@/components/features/movies/card/CopyToClipBoardButton";
import { HStack, useToast, VStack } from "@chakra-ui/react";
import { useState } from "react";
import { HiBookmark, HiDocumentCheck, HiHeart } from "react-icons/hi2";
import { createLogger } from "@/utils/logging";
import type { MovieDetailQuickActionProps } from "./types";

const logger = createLogger("MovieQuickAction");

const MovieQuickAction = ({
  movie,
  size = "sm",
  orientation = "vertical",
  toggleFunctions,
}: MovieDetailQuickActionProps) => {
  const Stack = orientation === "vertical" ? VStack : HStack;
  const toast = useToast();

  // Local loading states for immediate UI feedback
  const [loadingStates, setLoadingStates] = useState({
    watched: false,
    liked: false,
    watchlist: false,
  });

  const handleWatched = async () => {
    if (!toggleFunctions?.toggleWatched || loadingStates.watched) return;

    setLoadingStates((prev) => ({ ...prev, watched: true }));

    try {
      await toggleFunctions.toggleWatched();

      toast({
        title: `${!movie.watched ? "Added to" : "Removed from"} watched`,
        description: `${movie.title} was ${
          !movie.watched ? "marked as watched" : "unmarked as watched"
        }.`,
        status: "success",
        duration: 3000,
        isClosable: true,
        position: "bottom-right",
      });
    } catch (error) {
      logger.error(`Failed to toggle watched status:`, error);

      toast({
        title: "Action Failed",
        description: `Failed to update watched status for ${movie.title}.`,
        status: "error",
        duration: 3000,
        isClosable: true,
        position: "bottom-right",
      });
    } finally {
      setLoadingStates((prev) => ({ ...prev, watched: false }));
    }
  };

  const handleLiked = async () => {
    if (!toggleFunctions?.toggleLiked || loadingStates.liked) return;

    setLoadingStates((prev) => ({ ...prev, liked: true }));

    try {
      await toggleFunctions.toggleLiked();

      toast({
        title: `${!movie.liked ? "Added to" : "Removed from"} liked`,
        description: `${movie.title} was ${
          !movie.liked ? "added to" : "removed from"
        } your liked list.`,
        status: "success",
        duration: 3000,
        isClosable: true,
        position: "bottom-right",
      });
    } catch (error) {
      logger.error(`Failed to toggle liked status:`, error);

      toast({
        title: "Action Failed",
        description: `Failed to update liked status for ${movie.title}.`,
        status: "error",
        duration: 3000,
        isClosable: true,
        position: "bottom-right",
      });
    } finally {
      setLoadingStates((prev) => ({ ...prev, liked: false }));
    }
  };

  const handleWatchlist = async () => {
    if (!toggleFunctions?.toggleWatchlist || loadingStates.watchlist) return;

    setLoadingStates((prev) => ({ ...prev, watchlist: true }));

    try {
      await toggleFunctions.toggleWatchlist();

      toast({
        title: `${!movie.in_watchlist ? "Added to" : "Removed from"} watchlist`,
        description: `${movie.title} was ${
          !movie.in_watchlist ? "added to" : "removed from"
        } your watch list.`,
        status: "success",
        duration: 3000,
        isClosable: true,
        position: "bottom-right",
      });
    } catch (error) {
      logger.error(`Failed to toggle watchlist status:`, error);

      toast({
        title: "Action Failed",
        description: `Failed to update watchlist status for ${movie.title}.`,
        status: "error",
        duration: 3000,
        isClosable: true,
        position: "bottom-right",
      });
    } finally {
      setLoadingStates((prev) => ({ ...prev, watchlist: false }));
    }
  };

  return (
    <Stack>
      <ToggleIconButton
        isActive={Boolean(movie.in_watchlist)}
        onToggle={handleWatchlist}
        icon={<HiBookmark />}
        label="Add to Watch List"
        size={size}
        isLoading={loadingStates.watchlist}
      />
      <ToggleIconButton
        isActive={Boolean(movie.liked)}
        onToggle={handleLiked}
        icon={<HiHeart />}
        label="Mark as liked"
        size={size}
        isLoading={loadingStates.liked}
      />
      <ToggleIconButton
        isActive={Boolean(movie.watched)}
        onToggle={handleWatched}
        icon={<HiDocumentCheck />}
        label="Mark as watched"
        size={size}
        isLoading={loadingStates.watched}
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
