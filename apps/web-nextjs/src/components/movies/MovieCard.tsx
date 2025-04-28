"use client";

import { useState } from "react";
import {
  Box,
  Image,
  Text,
  Badge,
  Flex,
  useColorModeValue,
  IconButton,
  Tooltip,
} from "@chakra-ui/react";
import { HiStar, HiBookmark, HiCheck } from "react-icons/hi2";
import NextLink from "next/link";

interface Movie {
  id: string;
  title: string;
  poster_path: string;
  vote_average: number;
  release_date: string;
  genres?: string[];
}

interface MovieCardProps {
  movie: Movie;
  onFavoriteToggle?: (movieId: string) => void;
  onWatchlistToggle?: (movieId: string) => void;
  onWatchedToggle?: (movieId: string) => void;
  isFavorite?: boolean;
  isWatchlist?: boolean;
  isWatched?: boolean;
}

export default function MovieCard({
  movie,
  onFavoriteToggle,
  onWatchlistToggle,
  onWatchedToggle,
  isFavorite = false,
  isWatchlist = false,
  isWatched = false,
}: MovieCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const cardBg = useColorModeValue("white", "gray.800");
  const cardBorder = useColorModeValue("gray.200", "gray.700");

  // Format release year
  const year = movie.release_date
    ? new Date(movie.release_date).getFullYear()
    : "Unknown";

  // Format rating color
  const getRatingColor = (rating: number): string => {
    if (rating >= 7.5) return "green";
    if (rating >= 6) return "yellow";
    return "red";
  };

  return (
    <Box
      position="relative"
      borderRadius="lg"
      overflow="hidden"
      bg={cardBg}
      borderWidth="1px"
      borderColor={cardBorder}
      transition="all 0.3s"
      _hover={{
        transform: "translateY(-4px)",
        shadow: "lg",
        borderColor: "blue.400",
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <NextLink href={`/movies/${movie.id}`} passHref>
        <Box position="relative" cursor="pointer">
          <Image
            src={movie.poster_path}
            alt={movie.title}
            fallbackSrc="https://via.placeholder.com/300x450?text=No+Image"
            borderTopRadius="lg"
            width="100%"
            height="auto"
            objectFit="cover"
            aspectRatio="2/3"
          />

          {/* Rating badge */}
          <Badge
            position="absolute"
            top={2}
            right={2}
            colorScheme={getRatingColor(movie.vote_average)}
            fontSize="sm"
            borderRadius="full"
            px={2}
            py={1}
          >
            {movie.vote_average.toFixed(1)}
          </Badge>

          {/* Year badge */}
          <Badge
            position="absolute"
            bottom={2}
            right={2}
            colorScheme="blue"
            fontSize="sm"
            borderRadius="full"
            px={2}
            py={1}
          >
            {year}
          </Badge>

          {/* Overlay with buttons */}
          {isHovered && (
            <Flex
              position="absolute"
              top={2}
              left={2}
              direction="column"
              gap={2}
            >
              {onFavoriteToggle && (
                <Tooltip
                  label={
                    isFavorite ? "Remove from Favorites" : "Add to Favorites"
                  }
                >
                  <IconButton
                    aria-label="Toggle favorite"
                    icon={<HiStar />}
                    size="sm"
                    colorScheme={isFavorite ? "yellow" : "gray"}
                    onClick={(e) => {
                      e.preventDefault();
                      onFavoriteToggle(movie.id);
                    }}
                  />
                </Tooltip>
              )}

              {onWatchlistToggle && (
                <Tooltip
                  label={
                    isWatchlist ? "Remove from Watchlist" : "Add to Watchlist"
                  }
                >
                  <IconButton
                    aria-label="Toggle watchlist"
                    icon={<HiBookmark />}
                    size="sm"
                    colorScheme={isWatchlist ? "blue" : "gray"}
                    onClick={(e) => {
                      e.preventDefault();
                      onWatchlistToggle(movie.id);
                    }}
                  />
                </Tooltip>
              )}

              {onWatchedToggle && (
                <Tooltip
                  label={isWatched ? "Mark as Unwatched" : "Mark as Watched"}
                >
                  <IconButton
                    aria-label="Toggle watched"
                    icon={<HiCheck />}
                    size="sm"
                    colorScheme={isWatched ? "green" : "gray"}
                    onClick={(e) => {
                      e.preventDefault();
                      onWatchedToggle(movie.id);
                    }}
                  />
                </Tooltip>
              )}
            </Flex>
          )}
        </Box>
      </NextLink>

      <Box p={3}>
        <Text fontWeight="bold" fontSize="md" noOfLines={1} title={movie.title}>
          {movie.title}
        </Text>

        {movie.genres && movie.genres.length > 0 && (
          <Flex mt={1} gap={1} flexWrap="wrap">
            {movie.genres.slice(0, 2).map((genre) => (
              <Badge key={genre} colorScheme="gray" fontSize="xs">
                {genre}
              </Badge>
            ))}
          </Flex>
        )}
      </Box>
    </Box>
  );
}
