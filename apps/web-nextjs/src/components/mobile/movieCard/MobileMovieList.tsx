import React from "react";
import { VStack, Box, Text, Center, Spinner } from "@chakra-ui/react";
import { Movie } from "@/domain/entities";
import MobileMovieCard from "@/components/mobile/movieCard/MobileMovieCard";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("MobileMovieList");

interface MobileMovieListProps {
  movies: Movie[];
  isLoading: boolean;
  error: Error | null;
  onMovieUpdate: (movie: Movie) => void;
}

/**
 * MobileMovieList component
 * A mobile-optimized vertical list of movies with swipe actions
 * Provides better touch target sizes and interaction patterns than a grid
 */
const MobileMovieList: React.FC<MobileMovieListProps> = ({
  movies,
  isLoading,
  error,
  onMovieUpdate,
}) => {
  // Log component rendering
  logger.debug(`Rendering MobileMovieList with ${movies.length} movies`);

  if (isLoading) {
    return (
      <Center py={10}>
        <Spinner size="xl" thickness="4px" speed="0.65s" />
      </Center>
    );
  }

  if (error) {
    return (
      <Center py={10}>
        <Text color="red.500">Error loading movies: {error.message}</Text>
      </Center>
    );
  }

  if (movies.length === 0) {
    return (
      <Center py={10}>
        <Text>No movies found</Text>
      </Center>
    );
  }

  return (
    <VStack spacing={3} align="stretch" width="100%" pb={4}>
      {movies.map((movie) => (
        <Box
          key={
            typeof movie.id === "number" ? movie.id : `movie-${Math.random()}`
          }
        >
          <MobileMovieCard movie={movie} onMovieUpdate={onMovieUpdate} />
        </Box>
      ))}
    </VStack>
  );
};

export default MobileMovieList;
