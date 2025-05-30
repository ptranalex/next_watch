"use client";

import React from "react";
import {
  Box,
  Text,
  VStack,
  SimpleGrid,
  useBreakpointValue,
} from "@chakra-ui/react";
import MovieCard from "@/components/features/movies/card/MovieCard";
import { Movie } from "@/domain/entities/movies/Movie.entity";

interface SearchResultsProps {
  movies: Movie[];
  isLoading?: boolean;
  query: string;
}

/**
 * SearchResults - Display search results in a grid layout
 *
 * Displays search results using a responsive grid of movie cards.
 */
export function SearchResults({
  movies,
  isLoading = false,
  query,
}: SearchResultsProps): React.JSX.Element {
  const columns = useBreakpointValue({ base: 2, sm: 3, md: 4, lg: 5, xl: 6 });

  if (movies.length === 0 && !isLoading) {
    return (
      <Box textAlign="center" py={8}>
        <Text fontSize="lg" color="text.secondary">
          No movies found for &quot;{query}&quot;
        </Text>
      </Box>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Text fontSize="lg" fontWeight="semibold" mb={4}>
          Search Results ({movies.length} movies)
        </Text>
        <SimpleGrid columns={columns} spacing={4}>
          {movies.map((movie, index) => (
            <MovieCard
              key={`search-result-${index}`}
              movie={movie}
              onMovieUpdate={() => {
                // TODO: Implement movie update logic for search results
                // This could trigger a refetch of search results
              }}
            />
          ))}
        </SimpleGrid>
      </Box>
    </VStack>
  );
}
