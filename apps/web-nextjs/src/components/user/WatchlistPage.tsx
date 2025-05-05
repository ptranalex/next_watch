import React from "react";
import {
  Box,
  Heading,
  Text,
  SimpleGrid,
  Spinner,
  Center,
  Alert,
  AlertIcon,
} from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import { userInteractionAPI, MovieAPI } from "@/services/api";
import { Movie, toMovieEntity } from "@/domain/entities";
import MovieCard from "@/components/movieCard/MovieCard";

interface WatchlistPageProps {
  userId: string;
}

export const WatchlistPage: React.FC<WatchlistPageProps> = ({ userId }) => {
  // Fetch user's watchlist
  const { data, isLoading, error } = useQuery({
    queryKey: ["watchlist", userId],
    queryFn: async () => {
      // Get movies in watchlist first
      const interactions = await userInteractionAPI.getWatchlist();

      if (!interactions || interactions.length === 0) {
        return [];
      }

      // Fetch full details for each movie
      const movies: Movie[] = [];
      for (const interaction of interactions) {
        try {
          const movieData = await MovieAPI.getById(interaction.movie_id);
          if (movieData) {
            const movie = toMovieEntity(movieData);
            // Apply user interaction data
            movie.in_watchlist = true;
            movies.push(movie);
          }
        } catch (err) {
          console.error(`Failed to fetch movie ${interaction.movie_id}:`, err);
        }
      }

      return movies;
    },
  });

  if (isLoading) {
    return (
      <Center p={10}>
        <Spinner size="xl" />
      </Center>
    );
  }

  if (error) {
    return (
      <Alert status="error">
        <AlertIcon />
        Failed to load your watchlist. Please try again later.
      </Alert>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Box textAlign="center" p={10}>
        <Heading as="h1" mb={4}>
          Your Watchlist
        </Heading>
        <Text>You haven't added any movies to your watchlist yet.</Text>
      </Box>
    );
  }

  return (
    <Box>
      <Heading as="h1" mb={6}>
        Your Watchlist
      </Heading>
      <Text mb={6}>Movies you want to watch ({data.length})</Text>

      <SimpleGrid columns={{ base: 1, sm: 2, md: 3, lg: 4, xl: 5 }} spacing={4}>
        {data.map((movie) => (
          <MovieCard
            key={String(movie.id)}
            movie={movie}
            onMovieUpdate={() => {}} // Handle movie updates if needed
          />
        ))}
      </SimpleGrid>
    </Box>
  );
};
