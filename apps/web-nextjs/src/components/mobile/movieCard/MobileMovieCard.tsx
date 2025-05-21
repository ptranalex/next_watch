import React from "react";
import {
  Box,
  Image,
  Text,
  HStack,
  Icon,
  Flex,
  useColorModeValue,
  useToast,
} from "@chakra-ui/react";
import { Movie } from "@/domain/entities";
import { useQueryClient } from "@tanstack/react-query";
import { fetchData, userInteractionAPI } from "@/services/api";
import Link from "next/link";
import { HiMiniStar } from "react-icons/hi2";
import {
  HiHeart,
  HiOutlineHeart,
  HiOutlineBookmark,
  HiBookmark,
  HiOutlineCheck,
  HiCheck,
} from "react-icons/hi";
import SwipeAction, {
  SwipeActionOption,
} from "@/components/mobile/common/SwipeAction";
import { useAuth } from "@/hooks";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("MobileMovieCard");

interface MobileMovieCardProps {
  movie: Movie;
  onMovieUpdate: (movie: Movie) => void;
}

/**
 * MobileMovieCard component
 * Touch-optimized movie card with swipe actions for quick interactions
 * Swipe left to like, swipe right to add to watchlist
 */
const MobileMovieCard: React.FC<MobileMovieCardProps> = ({
  movie,
  onMovieUpdate,
}) => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const toast = useToast();
  const bgColor = useColorModeValue("white", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");

  const getColor = (value: number | undefined) => {
    if (!value) return "hidden";

    if (value >= 8.0) {
      return "***REMOVED***FFC107";
    } else if (value >= 7.0) {
      return "***REMOVED***00E676";
    } else if (value >= 6.0) {
      return "***REMOVED***82B1FF";
    }
    return "hidden";
  };

  const ratingColor = getColor(
    typeof movie.imdb_rating === "number" ? movie.imdb_rating : undefined
  );

  const prefetchMovieData = () => {
    if (typeof movie.id !== "number") return;

    logger.debug(`Prefetching data for movie ${movie.id}`);

    queryClient.prefetchQuery({
      queryKey: ["movie", movie.id],
      queryFn: () => fetchData(`/api/v1/movies/${movie.id}`),
    });

    queryClient.prefetchQuery({
      queryKey: ["movie", movie.id, "trailers"],
      queryFn: () => fetchData(`/api/v1/movies/${movie.id}/trailers`),
    });
  };

  // Handle toggling the liked status
  const handleToggleLiked = async () => {
    if (!user || typeof movie.id !== "number") return;

    const updatedMovie = { ...movie, liked: !movie.liked };

    try {
      // First update local state for immediate UI feedback
      onMovieUpdate(updatedMovie);

      // Then update server state
      logger.info(`Toggling liked state for movie ${movie.id}`, {
        liked: `${movie.liked} → ${updatedMovie.liked}`,
      });

      await userInteractionAPI.toggleLiked(movie.id);

      // Show toast notification
      toast({
        title: updatedMovie.liked
          ? "Added to favorites"
          : "Removed from favorites",
        status: updatedMovie.liked ? "success" : "info",
        duration: 2000,
        isClosable: true,
        position: "bottom",
      });

      // Invalidate relevant queries
      queryClient.invalidateQueries(["movie", movie.id]);
      queryClient.invalidateQueries(["favorites"]);
    } catch (error) {
      logger.error(`Failed to toggle liked for movie ${movie.id}:`, error);

      // Show error toast
      toast({
        title: "Update failed",
        description: "Failed to update favorite status.",
        status: "error",
        duration: 3000,
        isClosable: true,
        position: "bottom",
      });

      // Revert local state
      onMovieUpdate(movie);
    }
  };

  // Handle toggling the watchlist status
  const handleToggleWatchlist = async () => {
    if (!user || typeof movie.id !== "number") return;

    const updatedMovie = { ...movie, in_watchlist: !movie.in_watchlist };

    try {
      // First update local state for immediate UI feedback
      onMovieUpdate(updatedMovie);

      // Then update server state
      logger.info(`Toggling watchlist state for movie ${movie.id}`, {
        in_watchlist: `${movie.in_watchlist} → ${updatedMovie.in_watchlist}`,
      });

      await userInteractionAPI.toggleWatchlist(movie.id);

      // Show toast notification
      toast({
        title: updatedMovie.in_watchlist
          ? "Added to watchlist"
          : "Removed from watchlist",
        status: updatedMovie.in_watchlist ? "success" : "info",
        duration: 2000,
        isClosable: true,
        position: "bottom",
      });

      // Invalidate relevant queries
      queryClient.invalidateQueries(["movie", movie.id]);
      queryClient.invalidateQueries(["watchlist"]);
    } catch (error) {
      logger.error(`Failed to toggle watchlist for movie ${movie.id}:`, error);

      // Show error toast
      toast({
        title: "Update failed",
        description: "Failed to update watchlist status.",
        status: "error",
        duration: 3000,
        isClosable: true,
        position: "bottom",
      });

      // Revert local state
      onMovieUpdate(movie);
    }
  };

  // Handle toggling the watched status
  const handleToggleWatched = async () => {
    if (!user || typeof movie.id !== "number") return;

    const updatedMovie = { ...movie, watched: !movie.watched };

    try {
      // First update local state for immediate UI feedback
      onMovieUpdate(updatedMovie);

      // Then update server state
      logger.info(`Toggling watched state for movie ${movie.id}`, {
        watched: `${movie.watched} → ${updatedMovie.watched}`,
      });

      await userInteractionAPI.toggleWatched(movie.id);

      // Show toast notification
      toast({
        title: updatedMovie.watched
          ? "Marked as watched"
          : "Marked as unwatched",
        status: updatedMovie.watched ? "success" : "info",
        duration: 2000,
        isClosable: true,
        position: "bottom",
      });

      // Invalidate relevant queries
      queryClient.invalidateQueries(["movie", movie.id]);
      queryClient.invalidateQueries(["watched"]);
    } catch (error) {
      logger.error(`Failed to toggle watched for movie ${movie.id}:`, error);

      // Show error toast
      toast({
        title: "Update failed",
        description: "Failed to update watched status.",
        status: "error",
        duration: 3000,
        isClosable: true,
        position: "bottom",
      });

      // Revert local state
      onMovieUpdate(movie);
    }
  };

  // Define swipe actions
  const leftSwipeAction: SwipeActionOption = {
    icon: movie.liked ? HiHeart : HiOutlineHeart,
    label: movie.liked ? "Unfavorite" : "Favorite",
    color: "red.500",
    action: handleToggleLiked,
  };

  const rightSwipeAction: SwipeActionOption = {
    icon: movie.in_watchlist ? HiBookmark : HiOutlineBookmark,
    label: movie.in_watchlist ? "Remove" : "Watchlist",
    color: "blue.500",
    action: handleToggleWatchlist,
  };

  // Card content
  const cardContent = (
    <Box
      p={3}
      borderWidth="1px"
      borderColor={borderColor}
      borderRadius="md"
      bg={bgColor}
      width="100%"
    >
      <Flex>
        {/* Movie poster */}
        <Link
          href={`/movies/${movie.id}`}
          style={{ textDecoration: "none" }}
          onTouchStart={prefetchMovieData}
        >
          <Box position="relative" flexShrink={0}>
            <Image
              src={movie.poster_url as string}
              alt={`${movie.title} Poster`}
              width="80px"
              height="120px"
              objectFit="cover"
              borderRadius="md"
            />

            {/* Rating badge */}
            {ratingColor !== "hidden" && (
              <Flex
                position="absolute"
                top={1}
                left={1}
                bg="blackAlpha.700"
                borderRadius="full"
                width="28px"
                height="28px"
                justify="center"
                align="center"
              >
                <Icon as={HiMiniStar} color={ratingColor} boxSize={4} />
              </Flex>
            )}
          </Box>
        </Link>

        {/* Movie details */}
        <Flex direction="column" ml={4} flex={1} justifyContent="space-between">
          <Box>
            <Link
              href={`/movies/${movie.id}`}
              style={{ textDecoration: "none" }}
              onTouchStart={prefetchMovieData}
            >
              <Text fontWeight="bold" fontSize="md" noOfLines={2}>
                {movie.title}
              </Text>
            </Link>

            <Text fontSize="sm" color="gray.500" mt={1}>
              {typeof movie.release_date === "string"
                ? movie.release_date.substring(0, 4)
                : ""}
            </Text>
          </Box>

          {/* Action buttons */}
          <HStack spacing={2} mt={2}>
            <Box
              onClick={handleToggleWatched}
              p={2}
              borderRadius="md"
              bg={movie.watched ? "green.50" : "transparent"}
              _dark={{ bg: movie.watched ? "green.900" : "transparent" }}
              color={movie.watched ? "green.500" : "gray.500"}
            >
              <Icon as={movie.watched ? HiCheck : HiOutlineCheck} boxSize={5} />
            </Box>

            <Box
              onClick={handleToggleLiked}
              p={2}
              borderRadius="md"
              bg={movie.liked ? "red.50" : "transparent"}
              _dark={{ bg: movie.liked ? "red.900" : "transparent" }}
              color={movie.liked ? "red.500" : "gray.500"}
            >
              <Icon as={movie.liked ? HiHeart : HiOutlineHeart} boxSize={5} />
            </Box>

            <Box
              onClick={handleToggleWatchlist}
              p={2}
              borderRadius="md"
              bg={movie.in_watchlist ? "blue.50" : "transparent"}
              _dark={{ bg: movie.in_watchlist ? "blue.900" : "transparent" }}
              color={movie.in_watchlist ? "blue.500" : "gray.500"}
            >
              <Icon
                as={movie.in_watchlist ? HiBookmark : HiOutlineBookmark}
                boxSize={5}
              />
            </Box>
          </HStack>
        </Flex>
      </Flex>
    </Box>
  );

  if (!user) {
    return cardContent;
  }

  // Wrap card content with swipe actions
  return (
    <SwipeAction
      leftActions={[leftSwipeAction]}
      rightActions={[rightSwipeAction]}
    >
      {cardContent}
    </SwipeAction>
  );
};

export default MobileMovieCard;
