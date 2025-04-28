"use client";

import { useState, useEffect } from "react";
import {
  Box,
  Heading,
  Text,
  Center,
  Spinner,
  useToast,
} from "@chakra-ui/react";
import MovieGrid from "@/src/components/movies/MovieGrid";
import { HiBookmark } from "react-icons/hi2";

// Define a movie type that matches what MovieGrid expects
interface MovieGridItem {
  id: string;
  title: string;
  poster_path: string;
  vote_average: number;
  release_date: string;
  genres?: string[];
}

interface WatchlistProps {
  userId: string;
}

export default function Watchlist({ userId }: WatchlistProps) {
  const [movies, setMovies] = useState<MovieGridItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [watchlist, setWatchlist] = useState<Set<string>>(new Set());
  const toast = useToast();

  // Mock function to fetch watchlist data
  // In a real app, this would call an API endpoint
  useEffect(() => {
    const fetchWatchlist = async () => {
      try {
        setIsLoading(true);
        // This would be replaced with an actual API call
        // const response = await UserAPI.getWatchlist(userId);

        // Mock data for demonstration
        const mockWatchlistMovies = [
          {
            id: "1",
            title: "The Shawshank Redemption",
            poster_path: "/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
            vote_average: 8.7,
            release_date: "1994-09-23",
          },
          {
            id: "2",
            title: "The Godfather",
            poster_path: "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
            vote_average: 8.7,
            release_date: "1972-03-15",
          },
          {
            id: "3",
            title: "The Dark Knight",
            poster_path: "/1hRoyzDtpgMU7Dz4JF22RANzQO7.jpg",
            vote_average: 8.5,
            release_date: "2008-07-16",
          },
        ];

        setMovies(mockWatchlistMovies);

        // Initialize watchlist Set with movie IDs
        const watchlistIds = new Set(
          mockWatchlistMovies.map((movie) => movie.id)
        );
        setWatchlist(watchlistIds);

        setIsLoading(false);
      } catch (err) {
        setError(
          err instanceof Error ? err : new Error("Failed to fetch watchlist")
        );
        setIsLoading(false);
      }
    };

    fetchWatchlist();
  }, [userId]);

  const handleWatchlistToggle = (movieId: string) => {
    // Create a new set from the current watchlist
    const updatedWatchlist = new Set(watchlist);

    if (updatedWatchlist.has(movieId)) {
      // Remove from watchlist
      updatedWatchlist.delete(movieId);
      // In a real app, call API to remove from watchlist
      // await UserAPI.removeFromWatchlist(userId, movieId);

      // Remove the movie from the displayed list
      setMovies((prev) => prev.filter((movie) => movie.id !== movieId));

      toast({
        title: "Removed from watchlist",
        status: "info",
        duration: 2000,
        isClosable: true,
      });
    } else {
      // Add to watchlist (this would happen from other components)
      updatedWatchlist.add(movieId);
      // In a real app, call API to add to watchlist
      // await UserAPI.addToWatchlist(userId, movieId);

      toast({
        title: "Added to watchlist",
        status: "success",
        duration: 2000,
        isClosable: true,
      });
    }

    setWatchlist(updatedWatchlist);
  };

  if (isLoading) {
    return (
      <Center py={10}>
        <Spinner size="xl" />
      </Center>
    );
  }

  if (error) {
    return (
      <Center py={10}>
        <Text color="red.500">
          Error loading your watchlist: {error.message}
        </Text>
      </Center>
    );
  }

  return (
    <Box>
      <Heading as="h1" size="xl" mb={6} display="flex" alignItems="center">
        <HiBookmark style={{ marginRight: "0.5rem" }} />
        My Watchlist
      </Heading>

      {movies.length === 0 ? (
        <Center py={10}>
          <Text>Your watchlist is empty. Add movies to watch later!</Text>
        </Center>
      ) : (
        <MovieGrid
          movies={movies}
          onWatchlistToggle={handleWatchlistToggle}
          watchlist={watchlist}
        />
      )}
    </Box>
  );
}
