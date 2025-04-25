import React from "react";
import {
  Box,
  Heading,
  Text,
  SimpleGrid,
  Center,
  Spinner,
} from "@chakra-ui/react";
import MovieCard from "../MovieCard";
import { Movie } from "../../../services/movie-service";

interface RelatedMoviesProps {
  movies?: Movie[];
  isLoading: boolean;
}

const RelatedMovies: React.FC<RelatedMoviesProps> = ({ movies, isLoading }) => {
  return (
    <Box mb={8}>
      <Heading size="lg" mb={4}>
        Related Movies
      </Heading>
      {isLoading ? (
        <Center py={8}>
          <Spinner />
        </Center>
      ) : movies && movies.length > 0 ? (
        <SimpleGrid columns={{ base: 2, sm: 3, md: 4, lg: 5 }} spacing={4}>
          {movies.slice(0, 5).map((movie) => (
            <Box key={movie.id}>
              <MovieCard movie={movie} size="sm" />
            </Box>
          ))}
        </SimpleGrid>
      ) : (
        <Text color="gray.400">No related movies found.</Text>
      )}
    </Box>
  );
};

export default RelatedMovies;
