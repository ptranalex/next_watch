import React from "react";
import {
  Box,
  Image,
  Text,
  HStack,
  Icon,
  Flex,
  useColorModeValue,
  useMediaQuery,
  useBreakpointValue,
} from "@chakra-ui/react";
import { Movie } from "@/domain/entities";
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
import Link from "next/link";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("ResponsiveMovieCard");

interface ResponsiveMovieCardProps {
  movie: Movie;
  onMovieUpdate: (movie: Movie) => void;
  prefetchData?: () => void;
  showActions?: boolean;
}

/**
 * ResponsiveMovieCard component
 * Mobile-first movie card with progressive enhancement for desktop
 * The base design is optimized for mobile touch, with enhancements for desktop
 */
const ResponsiveMovieCard: React.FC<ResponsiveMovieCardProps> = ({
  movie,
  onMovieUpdate,
  prefetchData,
  showActions = true,
}) => {
  // Responsive adaptations
  const isDesktop = useBreakpointValue({ base: false, md: true });
  const [hasTouchScreen] = useMediaQuery("(pointer: coarse)");

  // Styling
  const bgColor = useColorModeValue("white", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");

  // Only use list view on mobile, grid view on desktop
  const isListView = !isDesktop;

  // Get the appropriate rating color
  const ratingColor = getRatingColor(
    typeof movie.imdb_rating === "number" ? movie.imdb_rating : undefined
  );

  // Define swipe actions for mobile
  const leftSwipeAction: SwipeActionOption = {
    icon: movie.liked ? HiHeart : HiOutlineHeart,
    label: movie.liked ? "Unfavorite" : "Favorite",
    color: "red.500",
    action: () => onMovieUpdate({ ...movie, liked: !movie.liked }),
  };

  const rightSwipeAction: SwipeActionOption = {
    icon: movie.in_watchlist ? HiBookmark : HiOutlineBookmark,
    label: movie.in_watchlist ? "Remove" : "Watchlist",
    color: "blue.500",
    action: () =>
      onMovieUpdate({ ...movie, in_watchlist: !movie.in_watchlist }),
  };

  // Handle prefetching movie data
  const handlePrefetch = () => {
    if (prefetchData) {
      prefetchData();
    }
  };

  // Base content (mobile optimized)
  const cardContent = isListView ? (
    // List view for mobile
    <Box
      p={3}
      borderWidth="1px"
      borderColor={borderColor}
      borderRadius="md"
      bg={bgColor}
      width="100%"
      transition="all 0.2s"
      _hover={isDesktop ? { transform: "translateY(-4px)", shadow: "md" } : {}}
    >
      <Flex>
        {/* Movie poster */}
        <Link
          href={`/movies/${movie.id}`}
          style={{ textDecoration: "none" }}
          onTouchStart={hasTouchScreen ? handlePrefetch : undefined}
          onMouseEnter={!hasTouchScreen ? handlePrefetch : undefined}
        >
          <Box position="relative" flexShrink={0}>
            <Image
              src={typeof movie.poster_url === "string" ? movie.poster_url : ""}
              alt={
                typeof movie.title === "string"
                  ? `${movie.title} Poster`
                  : "Movie Poster"
              }
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
              onTouchStart={hasTouchScreen ? handlePrefetch : undefined}
              onMouseEnter={!hasTouchScreen ? handlePrefetch : undefined}
            >
              <Text fontWeight="bold" fontSize="md" noOfLines={2}>
                {typeof movie.title === "string" ? movie.title : ""}
              </Text>
            </Link>

            <Text fontSize="sm" color="gray.500" mt={1}>
              {typeof movie.release_date === "string"
                ? movie.release_date.substring(0, 4)
                : ""}
            </Text>
          </Box>

          {/* Action buttons - only show if actions are enabled */}
          {showActions && (
            <HStack spacing={2} mt={2}>
              <Box
                onClick={() =>
                  onMovieUpdate({ ...movie, watched: !movie.watched })
                }
                p={2}
                borderRadius="md"
                bg={movie.watched ? "green.50" : "transparent"}
                _dark={{ bg: movie.watched ? "green.900" : "transparent" }}
                color={movie.watched ? "green.500" : "gray.500"}
              >
                <Icon
                  as={movie.watched ? HiCheck : HiOutlineCheck}
                  boxSize={5}
                />
              </Box>

              <Box
                onClick={() => onMovieUpdate({ ...movie, liked: !movie.liked })}
                p={2}
                borderRadius="md"
                bg={movie.liked ? "red.50" : "transparent"}
                _dark={{ bg: movie.liked ? "red.900" : "transparent" }}
                color={movie.liked ? "red.500" : "gray.500"}
              >
                <Icon as={movie.liked ? HiHeart : HiOutlineHeart} boxSize={5} />
              </Box>

              <Box
                onClick={() =>
                  onMovieUpdate({ ...movie, in_watchlist: !movie.in_watchlist })
                }
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
          )}
        </Flex>
      </Flex>
    </Box>
  ) : (
    // Grid view for desktop (enhancement)
    <Box
      borderRadius="lg"
      overflow="hidden"
      bg={bgColor}
      transition="all 0.2s"
      _hover={{ transform: "translateY(-4px)", shadow: "lg" }}
    >
      <Link
        href={`/movies/${movie.id}`}
        style={{ textDecoration: "none" }}
        onMouseEnter={handlePrefetch}
      >
        <Box position="relative">
          <Image
            src={typeof movie.poster_url === "string" ? movie.poster_url : ""}
            alt={
              typeof movie.title === "string"
                ? `${movie.title} Poster`
                : "Movie Poster"
            }
            width="100%"
            height="auto"
            aspectRatio="2 / 3"
            objectFit="cover"
          />

          {/* Rating badge */}
          {ratingColor !== "hidden" && (
            <Flex
              position="absolute"
              top={2}
              left={2}
              bg="blackAlpha.700"
              borderRadius="full"
              width="32px"
              height="32px"
              justify="center"
              align="center"
            >
              <Icon as={HiMiniStar} color={ratingColor} boxSize={5} />
            </Flex>
          )}

          {/* Action overlay (desktop enhancement) */}
          {showActions && (
            <Flex
              position="absolute"
              bottom={0}
              left={0}
              right={0}
              p={2}
              bg="blackAlpha.700"
              justifyContent="space-around"
              opacity={0}
              transition="opacity 0.2s"
              _groupHover={{ opacity: 1 }}
            >
              <Icon
                as={movie.watched ? HiCheck : HiOutlineCheck}
                color={movie.watched ? "green.300" : "white"}
                boxSize={6}
                cursor="pointer"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onMovieUpdate({ ...movie, watched: !movie.watched });
                }}
              />

              <Icon
                as={movie.liked ? HiHeart : HiOutlineHeart}
                color={movie.liked ? "red.300" : "white"}
                boxSize={6}
                cursor="pointer"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onMovieUpdate({ ...movie, liked: !movie.liked });
                }}
              />

              <Icon
                as={movie.in_watchlist ? HiBookmark : HiOutlineBookmark}
                color={movie.in_watchlist ? "blue.300" : "white"}
                boxSize={6}
                cursor="pointer"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onMovieUpdate({
                    ...movie,
                    in_watchlist: !movie.in_watchlist,
                  });
                }}
              />
            </Flex>
          )}
        </Box>
      </Link>

      <Box p={3}>
        <Text fontWeight="bold" fontSize="md" noOfLines={1}>
          {typeof movie.title === "string" ? movie.title : ""}
        </Text>
        <Text fontSize="sm" color="gray.500">
          {typeof movie.release_date === "string"
            ? movie.release_date.substring(0, 4)
            : ""}
        </Text>
      </Box>
    </Box>
  );

  // Apply swipe actions for mobile touch devices only
  if (hasTouchScreen && !isDesktop && showActions) {
    return (
      <SwipeAction
        leftActions={[leftSwipeAction]}
        rightActions={[rightSwipeAction]}
      >
        {cardContent}
      </SwipeAction>
    );
  }

  // Just return the card content for desktop
  return cardContent;
};

// Helper function to determine rating color
function getRatingColor(value: number | undefined): string {
  if (!value) return "hidden";

  if (value >= 8.0) {
    return "***REMOVED***FFC107"; // Gold for high ratings
  } else if (value >= 7.0) {
    return "***REMOVED***00E676"; // Green for good ratings
  } else if (value >= 6.0) {
    return "***REMOVED***82B1FF"; // Blue for decent ratings
  }
  return "hidden";
}

export default ResponsiveMovieCard;
