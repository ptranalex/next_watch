import { VStack, HStack, Box } from "@chakra-ui/react";
import { HiBookmark, HiDocumentCheck, HiHeart } from "react-icons/hi2";
import { Movie, toMovieEntity } from "@/domain/entities";
import CopyToClipboardButton from "./CopyToClipBoardButton";
import CardToggleIconButton from "./CardToggleIconButton";
import { userInteractionAPI } from "@/services/api";

interface Props {
  movie: Movie;
  onMovieUpdate: (updatedMovie: Movie) => void;
  size?: "sm" | "md" | "lg";
  orientation?: "vertical" | "horizontal";
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

  const handleWatched = async () => {
    const updatedMovie = {
      ...movie,
      is_watched: !movie.is_watched,
    };
    onMovieUpdate(updatedMovie);
  };

  const handleLiked = async () => {
    const updatedMovie = {
      ...movie,
      is_liked: !movie.is_liked,
    };
    onMovieUpdate(updatedMovie);
  };

  const handleToWatch = async () => {
    const updatedMovie = {
      ...movie,
      to_watch: !movie.to_watch,
    };
    onMovieUpdate(updatedMovie);
  };

  return (
    <Box
      flexGrow={1}
      background={isBlurred ? "rgba(0, 0, 0, 0.3)" : "transparent"}
      backdropFilter={isBlurred ? "blur(2x)" : "none"}
      transition="background 0.3s, backdrop-filter 0.3s"
      borderRadius="0"
      height="100%"
    >
      <Stack spacing={0} width="100%" height="100%" overflow="hidden">
        <CardToggleIconButton
          movie={movie}
          attribute="to_watch"
          endpoint="towatch"
          onToggle={handleToWatch}
          icon={<HiBookmark />}
          label="Add to Watch List"
          size={size}
          isEnabled={isBlurred}
        />
        <CardToggleIconButton
          movie={movie}
          attribute="is_liked"
          endpoint="liked"
          onToggle={handleLiked}
          icon={<HiHeart />}
          label="Mark as liked"
          size={size}
          isEnabled={isBlurred}
        />
        <CardToggleIconButton
          movie={movie}
          attribute="is_watched"
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
