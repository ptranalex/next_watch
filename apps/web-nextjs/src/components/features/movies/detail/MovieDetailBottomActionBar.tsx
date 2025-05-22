import React from "react";
import { Box, Flex, Icon, Text, useColorModeValue } from "@chakra-ui/react";
import {
  HiHeart,
  HiOutlineHeart,
  HiOutlineBookmark,
  HiBookmark,
  HiOutlineCheck,
  HiCheck,
  HiShare,
} from "react-icons/hi";
import { Movie } from "@/domain/entities";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("MovieDetailBottomActionBar");

interface MovieDetailBottomActionBarProps {
  movie: Movie;
  onUpdateMovie: (movie: Movie) => void;
  onShare?: () => void;
}

/**
 * MovieDetailBottomActionBar component
 * Provides easy access to primary movie actions for mobile users
 * Fixed at the bottom of the screen for easy thumb reach
 */
const MovieDetailBottomActionBar: React.FC<MovieDetailBottomActionBarProps> = ({
  movie,
  onUpdateMovie,
  onShare,
}) => {
  const bgColor = useColorModeValue("white", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");

  // Apply haptic feedback if available when buttons are pressed
  const applyHapticFeedback = () => {
    if (window.navigator && "vibrate" in window.navigator) {
      try {
        window.navigator.vibrate(30);
      } catch (e) {
        logger.warn("Vibration not supported", e);
      }
    }
  };

  // Handle watched toggle
  const handleWatchedToggle = () => {
    applyHapticFeedback();
    onUpdateMovie({ ...movie, watched: !movie.watched });
  };

  // Handle liked toggle
  const handleLikedToggle = () => {
    applyHapticFeedback();
    onUpdateMovie({ ...movie, liked: !movie.liked });
  };

  // Handle watchlist toggle
  const handleWatchlistToggle = () => {
    applyHapticFeedback();
    onUpdateMovie({ ...movie, in_watchlist: !movie.in_watchlist });
  };

  // Handle share
  const handleShare = () => {
    applyHapticFeedback();
    if (onShare) {
      onShare();
    } else if (navigator.share) {
      // Use web share API if available
      navigator
        .share({
          title: typeof movie.title === "string" ? movie.title : "Movie",
          text: `Check out this movie: ${
            typeof movie.title === "string" ? movie.title : "Movie"
          }`,
          url: window.location.href,
        })
        .then(() => logger.info("Shared successfully"))
        .catch((error) => logger.error("Error sharing:", error));
    }
  };

  return (
    <Box
      position="fixed"
      bottom={0}
      left={0}
      right={0}
      zIndex={10}
      bg={bgColor}
      borderTop="1px"
      borderColor={borderColor}
      py={2}
      px={4}
    >
      <Flex justify="space-around" align="center" width="100%">
        {/* Watched button */}
        <Flex
          direction="column"
          align="center"
          cursor="pointer"
          onClick={handleWatchedToggle}
          py={2}
          px={3}
          borderRadius="md"
          bg={movie.watched ? "green.50" : "transparent"}
          _dark={{ bg: movie.watched ? "green.900" : "transparent" }}
        >
          <Icon
            as={movie.watched ? HiCheck : HiOutlineCheck}
            boxSize={6}
            color={movie.watched ? "green.500" : "gray.500"}
            mb={1}
          />
          <Text
            fontSize="xs"
            color={movie.watched ? "green.500" : "gray.500"}
            fontWeight="medium"
          >
            {movie.watched ? "Watched" : "Watch"}
          </Text>
        </Flex>

        {/* Favorite button */}
        <Flex
          direction="column"
          align="center"
          cursor="pointer"
          onClick={handleLikedToggle}
          py={2}
          px={3}
          borderRadius="md"
          bg={movie.liked ? "red.50" : "transparent"}
          _dark={{ bg: movie.liked ? "red.900" : "transparent" }}
        >
          <Icon
            as={movie.liked ? HiHeart : HiOutlineHeart}
            boxSize={6}
            color={movie.liked ? "red.500" : "gray.500"}
            mb={1}
          />
          <Text
            fontSize="xs"
            color={movie.liked ? "red.500" : "gray.500"}
            fontWeight="medium"
          >
            {movie.liked ? "Favorited" : "Favorite"}
          </Text>
        </Flex>

        {/* Watchlist button */}
        <Flex
          direction="column"
          align="center"
          cursor="pointer"
          onClick={handleWatchlistToggle}
          py={2}
          px={3}
          borderRadius="md"
          bg={movie.in_watchlist ? "blue.50" : "transparent"}
          _dark={{ bg: movie.in_watchlist ? "blue.900" : "transparent" }}
        >
          <Icon
            as={movie.in_watchlist ? HiBookmark : HiOutlineBookmark}
            boxSize={6}
            color={movie.in_watchlist ? "blue.500" : "gray.500"}
            mb={1}
          />
          <Text
            fontSize="xs"
            color={movie.in_watchlist ? "blue.500" : "gray.500"}
            fontWeight="medium"
          >
            Watchlist
          </Text>
        </Flex>

        {/* Share button */}
        <Flex
          direction="column"
          align="center"
          cursor="pointer"
          onClick={handleShare}
          py={2}
          px={3}
          borderRadius="md"
        >
          <Icon as={HiShare} boxSize={6} color="gray.500" mb={1} />
          <Text fontSize="xs" color="gray.500" fontWeight="medium">
            Share
          </Text>
        </Flex>
      </Flex>
    </Box>
  );
};

export default MovieDetailBottomActionBar;
