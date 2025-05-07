import ScrollToTopButton from "@/components/commons/ScrollToTopButton";
import MovieCard from "@/components/movieCard/MovieCard";
import MovieCardContainer from "@/components/movieCard/MovieCardContainer";
import { Movie, toMovieEntity } from "@/domain/entities";
import { MovieAPI, userInteractionAPI } from "@/services/api";
import {
  Alert,
  AlertDescription,
  AlertIcon,
  Box,
  Center,
  SimpleGrid,
  Spinner,
  Text,
} from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import React, { useCallback } from "react";

interface WatchlistPageProps {
  userId: string;
}

export const WatchlistPage: React.FC<WatchlistPageProps> = ({ userId }) => {
  // Fetch user's watchlist with optimized stale time
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
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Memoized callback for handling movie updates
  const handleMovieUpdate = useCallback((movie: Movie) => {
    // In a real implementation, this would trigger a refetch or update local state
    console.log("Movie updated:", movie);
  }, []);

  if (isLoading) {
    return (
      <Center p={10}>
        <Spinner size="xl" thickness="4px" color="blue.500" />
      </Center>
    );
  }

  if (error) {
    return (
      <Alert
        status="error"
        variant="subtle"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        textAlign="center"
        py={4}
      >
        <AlertIcon boxSize="40px" mr={0} />
        <AlertDescription mt={3}>
          Failed to load your watchlist. Please try again later.
        </AlertDescription>
      </Alert>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Box textAlign="center" p={10}>
        <Text fontSize="lg">
          You haven&apos;t added any movies to your watchlist yet.
        </Text>
      </Box>
    );
  }

  return (
    <Box>
      <Text mb={6} fontSize="md">
        Movies you want to watch ({data.length})
      </Text>

      <Box position="relative">
        <SimpleGrid
          columns={{ base: 1, sm: 2, md: 3, lg: 4, xl: 5 }}
          spacing={3}
          padding={1}
        >
          {data.map((movie) => (
            <MovieCardContainer key={String(movie.id)}>
              <MovieCard movie={movie} onMovieUpdate={handleMovieUpdate} />
            </MovieCardContainer>
          ))}
        </SimpleGrid>
        <ScrollToTopButton />
      </Box>
    </Box>
  );
};
