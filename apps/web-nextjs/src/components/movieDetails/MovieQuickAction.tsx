import { VStack, HStack, useToast } from "@chakra-ui/react";
import { useState } from "react";
import { HiBookmark, HiDocumentCheck, HiHeart } from "react-icons/hi2";
import { Movie } from "@/domain/entities";
import CopyToClipboardButton from "../utils/CopyToClipBoardButton";
import ToggleIconButton from "../commons/ToggleIconButton";
import userInteractionAPI from "@/services/api/user/user-interaction-api";

interface Props {
  movie: Movie;
  onMovieUpdate: (updatedMovie: Movie) => void;
  size?: "sm" | "md" | "lg";
  orientation?: "vertical" | "horizontal";
}

const MovieQuickAction = ({
  movie,
  onMovieUpdate,
  size = "sm",
  orientation = "vertical",
}: Props) => {
  const Stack = orientation === "vertical" ? VStack : HStack;
  const toast = useToast();
  const [isLoadingWatched, setIsLoadingWatched] = useState(false);
  const [isLoadingLiked, setIsLoadingLiked] = useState(false);
  const [isLoadingInWatchlist, setIsLoadingInWatchlist] = useState(false);

  const handleWatched = async () => {
    if (isLoadingWatched) return;

    setIsLoadingWatched(true);
    const newValue = !movie.watched;

    try {
      // Optimistic update
      const updatedMovie = { ...movie, watched: newValue };
      onMovieUpdate(updatedMovie);

      // API call
      await userInteractionAPI.toggleWatched(movie.id as number);

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
      const revertedMovie = { ...movie, watched: !newValue };
      onMovieUpdate(revertedMovie);

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
    }
  };

  const handleLiked = async () => {
    if (isLoadingLiked) return;

    setIsLoadingLiked(true);
    const newValue = !movie.liked;

    try {
      // Optimistic update
      const updatedMovie = { ...movie, liked: newValue };
      onMovieUpdate(updatedMovie);

      // API call
      await userInteractionAPI.toggleLiked(movie.id as number);

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
      const revertedMovie = { ...movie, liked: !newValue };
      onMovieUpdate(revertedMovie);

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
    }
  };

  const handleInWatchlist = async () => {
    if (isLoadingInWatchlist) return;

    setIsLoadingInWatchlist(true);
    const newValue = !movie.in_watchlist;

    try {
      // Optimistic update
      const updatedMovie = { ...movie, in_watchlist: newValue };
      onMovieUpdate(updatedMovie);

      // API call
      await userInteractionAPI.toggleWatchlist(movie.id as number);

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
      const revertedMovie = { ...movie, in_watchlist: !newValue };
      onMovieUpdate(revertedMovie);

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
