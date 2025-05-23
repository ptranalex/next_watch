import CardToggleIconButton from "./CardToggleIconButton";
import CopyToClipboardButton from "./CopyToClipBoardButton";
import { Movie } from "@/domain/entities";
import { Box, HStack, VStack, useColorModeValue } from "@chakra-ui/react";
import { HiBookmark, HiDocumentCheck, HiHeart } from "react-icons/hi2";
import type {
  ComponentSize,
  MovieCardOrientation,
  MovieUpdateCallback,
} from "./types";

interface Props {
  movie: Movie;
  onMovieUpdate: MovieUpdateCallback;
  size?: ComponentSize;
  orientation?: MovieCardOrientation;
  isHovered: boolean; // Prop to indicate blur effect
}

const MovieQuickAction = ({
  movie,
  onMovieUpdate,
  size = "sm",
  orientation = "vertical",
  isHovered: isBlurred,
}: Props) => {
  const Stack = orientation === "vertical" ? VStack : HStack;
  const overlayBg = useColorModeValue(
    "rgba(0, 0, 0, 0.15)",
    "rgba(0, 0, 0, 0.6)"
  );

  const handleWatched = async () => {
    const updatedMovie = {
      ...movie,
      watched: !movie.watched,
    };
    onMovieUpdate(updatedMovie);
  };

  const handleLiked = async () => {
    const updatedMovie = {
      ...movie,
      liked: !movie.liked,
    };
    onMovieUpdate(updatedMovie);
  };

  const handleToWatch = async () => {
    const updatedMovie = {
      ...movie,
      in_watchlist: !movie.in_watchlist,
    };
    onMovieUpdate(updatedMovie);
  };

  return (
    <Box
      flexGrow={1}
      background={isBlurred ? overlayBg : "transparent"}
      backdropFilter={isBlurred ? "blur(2px)" : "none"}
      transition="background 0.3s, backdrop-filter 0.3s"
      borderRadius="0"
      height="100%"
    >
      <Stack spacing={0} width="100%" height="100%" overflow="hidden">
        <CardToggleIconButton
          movie={movie}
          attribute="in_watchlist"
          endpoint="towatch"
          onToggle={handleToWatch}
          icon={<HiBookmark />}
          label="Add to Watch List"
          size={size}
          isEnabled={isBlurred}
        />
        <CardToggleIconButton
          movie={movie}
          attribute="liked"
          endpoint="liked"
          onToggle={handleLiked}
          icon={<HiHeart />}
          label="Mark as liked"
          size={size}
          isEnabled={isBlurred}
        />
        <CardToggleIconButton
          movie={movie}
          attribute="watched"
          endpoint="watched"
          onToggle={handleWatched}
          icon={<HiDocumentCheck />}
          label="Mark as watched"
          size={size}
          isEnabled={isBlurred}
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
