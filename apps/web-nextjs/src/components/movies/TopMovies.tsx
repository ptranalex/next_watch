"use client";

import { useState, useEffect } from "react";
import {
  Box,
  Heading,
  Alert,
  AlertIcon,
  Spinner,
  Flex,
  Select,
  Text,
} from "@chakra-ui/react";
import useTopMovies from "@/src/hooks/useTopMovies";
import MovieGrid from "./MovieGrid";

// Type definition for movies in the grid
interface Movie {
  id: string;
  title: string;
  poster_path: string;
  vote_average: number;
  release_date: string;
  genres?: string[];
}

interface TopMoviesProps {
  title?: string;
  initialYear?: number;
  showYearSelector?: boolean;
  isAllTime?: boolean;
  genreId?: number;
  limit?: number;
}

export default function TopMovies({
  title = "Top Movies",
  initialYear = new Date().getFullYear(),
  showYearSelector = true,
  isAllTime = false,
  genreId,
  limit = 10,
}: TopMoviesProps) {
  const currentYear = new Date().getFullYear();
  const [selectedYear, setSelectedYear] = useState(initialYear);
  const [page, setPage] = useState(1);

  // If isAllTime is true, year doesn't matter
  const yearForQuery = isAllTime ? undefined : selectedYear;

  const { data, isLoading, error, isFetching } = useTopMovies(
    yearForQuery,
    isAllTime,
    genreId,
    limit,
    page
  );

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [selectedYear, isAllTime, genreId]);

  // Generate year options for the dropdown
  const yearOptions = [];
  for (let year = currentYear; year >= 1990; year--) {
    yearOptions.push(year);
  }

  // Handle loading state
  if (isLoading) {
    return (
      <Box textAlign="center" py={6}>
        <Spinner size="lg" />
      </Box>
    );
  }

  // Handle error state
  if (error) {
    return (
      <Alert status="error" my={4}>
        <AlertIcon />
        Error loading top movies:{" "}
        {error instanceof Error ? error.message : "Unknown error"}
      </Alert>
    );
  }

  // Format movie data for MovieGrid
  const formatMovieData = (): Movie[] => {
    if (!data || !data.movies) return [];

    return data.movies.map((movie) => ({
      id: movie.id.toString(),
      title: movie.title,
      poster_path: movie.poster_path || "/placeholder-poster.jpg",
      vote_average: movie.vote_average || 0,
      release_date: movie.release_date || "",
      genres: movie.genres ? movie.genres.map((g) => g.name) : [],
    }));
  };

  const formattedMovies = formatMovieData();

  // Handle empty state
  if (formattedMovies.length === 0) {
    return (
      <Box my={6}>
        <Flex justify="space-between" align="center" mb={4}>
          <Heading as="h2" size="lg">
            {title}
          </Heading>
          {showYearSelector && !isAllTime && (
            <Select
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              width="auto"
              ml={2}
            >
              {yearOptions.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </Select>
          )}
        </Flex>
        <Alert status="info">
          <AlertIcon />
          No top movies found for the selected criteria.
        </Alert>
      </Box>
    );
  }

  // Handle more button click
  const handleLoadMore = () => {
    setPage((prevPage) => prevPage + 1);
  };

  // Check if there are more pages to load
  const hasMore = data && data.page * data.page_size < data.total;

  return (
    <Box my={6}>
      <Flex justify="space-between" align="center" mb={4}>
        <Heading as="h2" size="lg">
          {title}
        </Heading>
        {showYearSelector && !isAllTime && (
          <Select
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            width="auto"
            ml={2}
          >
            {yearOptions.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </Select>
        )}
      </Flex>

      <MovieGrid
        movies={formattedMovies}
        isLoading={false}
        hasMoreMovies={hasMore}
        onLoadMore={handleLoadMore}
        isLoadingMore={isFetching}
      />

      {data && (
        <Text fontSize="sm" color="gray.500" textAlign="right" mt={2}>
          Showing {formattedMovies.length} of {data.total} movies
        </Text>
      )}
    </Box>
  );
}
