"use client";

import { useState } from "react";
import {
  Box,
  Container,
  Heading,
  Flex,
  Spacer,
  Input,
  IconButton,
  InputGroup,
  InputLeftElement,
  Select,
  useBreakpointValue,
} from "@chakra-ui/react";
import { HiSearch, HiFilter } from "react-icons/hi";
import MovieGrid from "@/src/components/movies/MovieGrid";
import ScrollToTopButton from "@/src/components/common/ScrollToTopButton";
import ColorModeSwitch from "@/src/components/common/ColorModeSwitch";
import { useMovies } from "@/src/hooks/useMovies";

export default function MoviesPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("popularity");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const isMobile = useBreakpointValue({ base: true, md: false });

  // Handle search input with debounce
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchQuery(value);

    // Debounce search query to avoid unnecessary API calls
    clearTimeout(Number(sessionStorage.getItem("searchTimer")));
    const timer = setTimeout(() => {
      setDebouncedSearch(value);
    }, 500);
    sessionStorage.setItem("searchTimer", timer.toString());
  };

  // Use our custom hook to fetch movies
  const { movies, isLoading, error, loadMore, hasMore, isLoadingMore } =
    useMovies({
      searchQuery: debouncedSearch,
      sortBy: sortBy,
    });

  return (
    <Container maxW="container.xl" py={8}>
      <Flex
        direction={{ base: "column", md: "row" }}
        align={{ base: "stretch", md: "center" }}
        mb={8}
        gap={4}
      >
        <Heading as="h1" size="xl">
          Movies
        </Heading>

        <Spacer />

        <Flex gap={4} width={{ base: "100%", md: "auto" }}>
          {/* Search input */}
          <InputGroup maxW={{ base: "100%", md: "300px" }}>
            <InputLeftElement pointerEvents="none">
              <HiSearch color="gray.300" />
            </InputLeftElement>
            <Input
              placeholder="Search movies"
              value={searchQuery}
              onChange={handleSearch}
            />
          </InputGroup>

          {/* Sort select */}
          <Select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            width={{ base: "full", md: "200px" }}
          >
            <option value="popularity">Popularity</option>
            <option value="release_date">Release Date</option>
            <option value="vote_average">Rating</option>
            <option value="title">Title</option>
          </Select>

          {/* Filter button (mobile) */}
          {isMobile && (
            <IconButton
              aria-label="Filter movies"
              icon={<HiFilter />}
              variant="outline"
            />
          )}

          {/* Color mode switch */}
          <ColorModeSwitch showLabel={false} />
        </Flex>
      </Flex>

      {/* Movies grid */}
      <Box position="relative">
        <MovieGrid
          movies={movies}
          isLoading={isLoading}
          error={error}
          onLoadMore={loadMore}
          hasMoreMovies={hasMore}
          isLoadingMore={isLoadingMore}
        />
      </Box>

      {/* Scroll to top button */}
      <ScrollToTopButton />
    </Container>
  );
}
