import React from "react";
import {
  SimpleGrid,
  Box,
  Text,
  Spinner,
  Center,
  Button,
} from "@chakra-ui/react";
import { Movie } from "../../services/movie-service";
import MovieCard from "./MovieCard";

interface MovieGridProps {
  movies: Movie[];
  isLoading?: boolean;
  hasMore?: boolean;
  onLoadMore?: () => void;
  columns?: { base: number; sm: number; md: number; lg: number; xl?: number };
}

const MovieGrid: React.FC<MovieGridProps> = ({
  movies,
  isLoading = false,
  hasMore = false,
  onLoadMore,
  columns = { base: 2, sm: 2, md: 3, lg: 4, xl: 5 },
}) => {
  if (isLoading && (!movies || movies.length === 0)) {
    return (
      <Center py={12}>
        <Spinner size="xl" color="blue.400" />
      </Center>
    );
  }

  if (!movies || movies.length === 0) {
    return (
      <Center py={12}>
        <Text>No movies found</Text>
      </Center>
    );
  }

  return (
    <Box>
      <SimpleGrid columns={columns} spacing={6} py={4} justifyItems="center">
        {movies.map((movie) => (
          <MovieCard key={movie.id} movie={movie} />
        ))}
      </SimpleGrid>

      {hasMore && onLoadMore && (
        <Center py={8}>
          <Button
            colorScheme="blue"
            onClick={onLoadMore}
            isLoading={isLoading}
            loadingText="Loading more"
          >
            Load More
          </Button>
        </Center>
      )}
    </Box>
  );
};

export default MovieGrid;
