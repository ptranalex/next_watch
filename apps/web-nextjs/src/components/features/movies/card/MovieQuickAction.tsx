import CardToggleIconButton from "./CardToggleIconButton";
import CopyToClipboardButton from "./CopyToClipBoardButton";
import { Movie } from "@/domain/entities";
import {
  Box,
  HStack,
  VStack,
  useColorModeValue,
  useToast,
} from "@chakra-ui/react";
import { HiBookmark, HiDocumentCheck, HiHeart } from "react-icons/hi2";
import { useState } from "react";
import { createLogger } from "@/utils/logging";
import type { ComponentSize, MovieCardOrientation } from "./types";

const logger = createLogger("MovieQuickAction");

interface Props {
  movie: Movie;
  size?: ComponentSize;
  orientation?: MovieCardOrientation;
  isHovered?: boolean;
  toggleFunctions?: {
    toggleWatched?: () => Promise<void>;
    toggleLiked?: () => Promise<void>;
    toggleWatchlist?: () => Promise<void>;
  };
}

const MovieQuickAction = ({
  movie,
  size = "sm",
  orientation = "vertical",
  isHovered: parentIsHovered,
  toggleFunctions,
}: Props) => {
  const [internalIsHovered, setInternalIsHovered] = useState(false);
  const Stack = orientation === "vertical" ? VStack : HStack;
  const toast = useToast();

  // Use parent hover state if provided, otherwise fall back to internal state
  const isHovered =
    parentIsHovered !== undefined ? parentIsHovered : internalIsHovered;

  // Local loading states for immediate UI feedback
  const [loadingStates, setLoadingStates] = useState({
    watched: false,
    liked: false,
    watchlist: false,
  });

  const overlayBg = useColorModeValue(
    "rgba(0, 0, 0, 0.15)",
    "rgba(0, 0, 0, 0.6)"
  );

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
    <Box
      flexGrow={1}
      background={isHovered ? overlayBg : "transparent"}
      backdropFilter={isHovered ? "blur(2px)" : "none"}
      transition="background 0.3s, backdrop-filter 0.3s"
      borderRadius="0"
      height="100%"
      onMouseEnter={() =>
        parentIsHovered === undefined && setInternalIsHovered(true)
      }
      onMouseLeave={() =>
        parentIsHovered === undefined && setInternalIsHovered(false)
      }
    >
      <Stack spacing={0} width="100%" height="100%" overflow="hidden">
        <CardToggleIconButton
          isActive={Boolean(movie.in_watchlist)}
          onToggle={handleWatchlist}
          icon={<HiBookmark />}
          label="Add to Watch List"
          size={size}
          isEnabled={isHovered}
          isLoading={loadingStates.watchlist}
        />
        <CardToggleIconButton
          isActive={Boolean(movie.liked)}
          onToggle={handleLiked}
          icon={<HiHeart />}
          label="Mark as liked"
          size={size}
          isEnabled={isHovered}
          isLoading={loadingStates.liked}
        />
        <CardToggleIconButton
          isActive={Boolean(movie.watched)}
          onToggle={handleWatched}
          icon={<HiDocumentCheck />}
          label="Mark as watched"
          size={size}
          isEnabled={isHovered}
          isLoading={loadingStates.watched}
        />
        <Box height="100%" width="100%" flexGrow={1} borderRadius={0}>
          {movie.fshare_link && typeof movie.fshare_link === "string" && (
            <CopyToClipboardButton
              textToCopy={movie.fshare_link}
              label="Copy fshare link to clipboard"
              size={size}
            />
          )}
        </Box>
      </Stack>
    </Box>
  );
};

export default MovieQuickAction;
