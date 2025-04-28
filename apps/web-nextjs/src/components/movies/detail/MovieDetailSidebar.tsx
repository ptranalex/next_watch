"use client";

import { useState, useEffect } from "react";
import {
  Box,
  VStack,
  Heading,
  Text,
  Button,
  Divider,
  Spinner,
  Badge,
} from "@chakra-ui/react";
import { FaHeart, FaBookmark, FaShare } from "react-icons/fa";

interface MovieDetailSidebarProps {
  movieId: string;
}

interface MovieMetadata {
  director: string;
  writers: string[];
  stars: string[];
  ratings: {
    imdb: number;
    rottenTomatoes: number;
    metacritic: number;
  };
}

const MovieDetailSidebar: React.FC<MovieDetailSidebarProps> = ({ movieId }) => {
  const [metadata, setMetadata] = useState<MovieMetadata | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isFavorite, setIsFavorite] = useState(false);
  const [isWatchlist, setIsWatchlist] = useState(false);

  useEffect(() => {
    // This would be replaced with a real API call
    const fetchMetadata = async () => {
      setIsLoading(true);
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 1200));

      // Mock data
      setMetadata({
        director: "Sample Director",
        writers: ["Writer 1", "Writer 2"],
        stars: ["Actor 1", "Actor 2", "Actor 3"],
        ratings: {
          imdb: 7.5,
          rottenTomatoes: 85,
          metacritic: 75,
        },
      });
      setIsLoading(false);
    };

    fetchMetadata();
  }, [movieId]);

  if (isLoading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="md" />
      </Box>
    );
  }

  if (!metadata) {
    return <Box>Metadata not available</Box>;
  }

  const toggleFavorite = () => setIsFavorite(!isFavorite);
  const toggleWatchlist = () => setIsWatchlist(!isWatchlist);

  return (
    <VStack
      spacing={4}
      align="stretch"
      p={4}
      borderWidth="1px"
      borderRadius="md"
    >
      <Heading size="md">Movie Actions</Heading>

      <VStack spacing={2}>
        <Button
          leftIcon={<FaHeart />}
          colorScheme={isFavorite ? "red" : "gray"}
          variant="outline"
          width="100%"
          onClick={toggleFavorite}
        >
          {isFavorite ? "Remove from Favorites" : "Add to Favorites"}
        </Button>

        <Button
          leftIcon={<FaBookmark />}
          colorScheme={isWatchlist ? "blue" : "gray"}
          variant="outline"
          width="100%"
          onClick={toggleWatchlist}
        >
          {isWatchlist ? "Remove from Watchlist" : "Add to Watchlist"}
        </Button>

        <Button
          leftIcon={<FaShare />}
          colorScheme="teal"
          variant="outline"
          width="100%"
        >
          Share
        </Button>
      </VStack>

      <Divider />

      <Heading size="sm">Ratings</Heading>
      <Box>
        <Badge colorScheme="yellow" fontSize="0.9em" mr={2}>
          IMDb: {metadata.ratings.imdb}/10
        </Badge>
        <Badge colorScheme="red" fontSize="0.9em" mr={2}>
          Rotten Tomatoes: {metadata.ratings.rottenTomatoes}%
        </Badge>
        <Badge colorScheme="green" fontSize="0.9em">
          Metacritic: {metadata.ratings.metacritic}/100
        </Badge>
      </Box>

      <Divider />

      <Box>
        <Text fontWeight="bold">Director</Text>
        <Text>{metadata.director}</Text>
      </Box>

      <Box>
        <Text fontWeight="bold">Writers</Text>
        <Text>{metadata.writers.join(", ")}</Text>
      </Box>

      <Box>
        <Text fontWeight="bold">Stars</Text>
        <Text>{metadata.stars.join(", ")}</Text>
      </Box>
    </VStack>
  );
};

export default MovieDetailSidebar;
