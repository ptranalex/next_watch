"use client";

import React, { useState, useCallback, useEffect } from "react";
import {
  Box,
  Container,
  VStack,
  HStack,
  Text,
  useColorModeValue,
  Alert,
  AlertIcon,
  Spinner,
  Center,
  Flex,
  useBreakpointValue,
} from "@chakra-ui/react";
import { SearchFilters } from "@/components/features/search/SearchFilters";
import MovieGrid from "@/components/features/movies/grid/MovieGrid";
import { MovieSortSelector } from "@/components/ui/molecules/SortSelector";
import { useInfiniteSearch } from "@/services/hooks/domain/search/useSearch";
import { useRouter, useSearchParams } from "next/navigation";
import { createLogger } from "@/utils/logging";

const logger = createLogger("SearchPage");

/**
 * SearchPage - Main search interface component
 *
 * This is a feature-level component that contains all the business logic
 * for search functionality, filtering, pagination, and state management.
 *
 * Provides a comprehensive search experience with:
 * - Advanced filtering options
 * - Paginated results
 * - Responsive design for mobile and desktop
 * - URL state management for shareable search results
 *
 * Note: Search input is handled by the main layout/navigation
 */
export function SearchPage(): React.JSX.Element {
  // Log component initialization
  logger.debug("SearchPage feature component initializing");

  const router = useRouter();
  const searchParams = useSearchParams();

  // Get current values from URL params (reactive to changes)
  const query = searchParams.get("q") || "";
  const urlPage = parseInt(searchParams.get("page") || "1");
  const urlGenreId = searchParams.get("genre_id")
    ? parseInt(searchParams.get("genre_id")!)
    : undefined;
  const urlYear = searchParams.get("year")
    ? parseInt(searchParams.get("year")!)
    : undefined;
  const urlSortBy = searchParams.get("sort_by") || "title";
  const urlSortDesc = searchParams.get("sort_desc") === "true";

  // Local state for search parameters (synced with URL)
  const [page, setPage] = useState(urlPage);
  const [genreId, setGenreId] = useState(urlGenreId);
  const [year, setYear] = useState(urlYear);
  const [sortBy, setSortBy] = useState(urlSortBy);
  const [sortDesc, setSortDesc] = useState(urlSortDesc);
  const [showFilters, setShowFilters] = useState(false);

  // Sync local state with URL parameters when they change
  useEffect(() => {
    setPage(urlPage);
    setGenreId(urlGenreId);
    setYear(urlYear);
    setSortBy(urlSortBy);
    setSortDesc(urlSortDesc);
  }, [urlPage, urlGenreId, urlYear, urlSortBy, urlSortDesc]);
  // Theme colors
  const bgColor = useColorModeValue("bg.primary", "bg.primary");
  const borderColor = useColorModeValue("border.subtle", "border.subtle");

  // Responsive layout
  const isMobile = useBreakpointValue({ base: true, md: false });
  const containerPadding = useBreakpointValue({ base: 4, md: 8 });

  // Use the infinite search hook
  const {
    movies,
    totalMovies,
    fetchedMoviesCount,
    hasNextPage,
    fetchNextPage,
    error,
    isLoading,
    isFetching,
    isFetchingNextPage,
  } = useInfiniteSearch({
    query,
    genreId,
    year,
    sortBy,
    sortDesc,
  });

  // Handle load more for infinite scrolling
  const handleLoadMore = useCallback(async () => {
    if (hasNextPage && !isFetchingNextPage) {
      await fetchNextPage();
    }
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  // Update URL when search parameters change
  const updateURL = useCallback(
    (params: Record<string, string | number | boolean | undefined>) => {
      const url = new URLSearchParams();

      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== "" && value !== null) {
          url.set(key, value.toString());
        }
      });

      const urlString = url.toString();
      const newUrl = urlString ? `/search?${urlString}` : "/search";

      router.push(newUrl, { scroll: false });
    },
    [router]
  );

  // Handle filter changes
  const handleFiltersChange = useCallback(
    (filters: {
      genreId?: number;
      year?: number;
      sortBy?: string;
      sortDesc?: boolean;
    }) => {
      setGenreId(filters.genreId);
      setYear(filters.year);
      setSortBy(filters.sortBy || "title");
      setSortDesc(filters.sortDesc || false);
      setPage(1); // Reset to first page on filter change

      updateURL({
        q: query,
        page: 1,
        genre_id: filters.genreId,
        year: filters.year,
        sort_by: filters.sortBy,
        sort_desc: filters.sortDesc,
      });
    },
    [query, updateURL]
  );

  // Handle clear filters
  const handleClearFilters = useCallback(() => {
    setGenreId(undefined);
    setYear(undefined);
    setSortBy("title");
    setSortDesc(false);
    setPage(1);

    updateURL({
      q: query,
      page: 1,
    });
  }, [query, updateURL]);

  // Computed values
  const hasResults: boolean = movies.length > 0;
  const hasQuery: boolean = query.length > 0;
  const hasError: boolean = Boolean(error);
  const showNoResults: boolean =
    hasQuery && !isLoading && !hasResults && !hasError;
  const showResults: boolean = hasQuery && hasResults;

  // Log search activity
  useEffect(() => {
    if (query && movies.length > 0) {
      logger.info(
        `Search results loaded: ${movies.length} movies for query: "${query}"`
      );
    }
  }, [query, movies]);

  logger.debug("SearchPage render", {
    query,
    page,
    totalMovies,
    hasResults,
    isLoading,
    isFetching,
  });

  return (
    <Box bg={bgColor} minH="100vh">
      <Container maxW="7xl" px={containerPadding} py={8}>
        <VStack spacing={8} align="stretch">
          {/* Search Header */}
          {hasQuery && (
            <VStack spacing={4} align="stretch">
              <Box>
                <Text fontSize="3xl" fontWeight="bold" mb={2}>
                  Search Results
                </Text>
                <Text color="text.secondary" fontSize="lg">
                  {isLoading ? "Searching..." : `Results for "${query}"`}
                </Text>
              </Box>
            </VStack>
          )}

          {/* Empty State - No Search Query */}
          {!hasQuery && (
            <Center py={20}>
              <VStack spacing={4} textAlign="center">
                <Text fontSize="2xl" fontWeight="semibold">
                  Search Movies
                </Text>
                <Text color="text.secondary" maxW="md">
                  Use the search bar above to find movies by title, actor, or
                  genre.
                </Text>
                <Text color="text.muted" fontSize="sm">
                  Try searching for &quot;batman&quot;, &quot;comedy&quot;, or
                  your favorite actor
                </Text>
              </VStack>
            </Center>
          )}

          {/* Search Filters - only show when there's a query */}
          {hasQuery && (
            <>
              <SearchFilters
                genreId={genreId}
                year={year}
                sortBy={sortBy}
                sortDesc={sortDesc}
                showFilters={showFilters}
                onToggleFilters={() => setShowFilters(!showFilters)}
                onFiltersChange={handleFiltersChange}
                onClearFilters={handleClearFilters}
                isMobile={isMobile ?? false}
              />
            </>
          )}

          {/* Search Status and Sort */}
          {hasQuery && (
            <Flex
              justify="space-between"
              align="center"
              borderY="1px"
              borderColor={borderColor}
              py={4}
            >
              <Box>
                <Text fontSize="lg" fontWeight="semibold">
                  {isLoading ? "Searching..." : `Search results for "${query}"`}
                </Text>
                {!isLoading && totalMovies > 0 && (
                  <Text color="text.secondary" fontSize="sm">
                    {totalMovies} movie{totalMovies !== 1 ? "s" : ""} found
                  </Text>
                )}
              </Box>

              <HStack spacing={4}>
                {/* Sort Selector */}
                {!isLoading && hasResults && (
                  <MovieSortSelector
                    currentSortOrder={sortBy}
                    currentSortDesc={sortDesc}
                    onSortChange={(value, desc) => {
                      handleFiltersChange({
                        genreId,
                        year,
                        sortBy: value,
                        sortDesc: desc,
                      });
                    }}
                    size="sm"
                  />
                )}

                {isFetching && (
                  <HStack spacing={2}>
                    <Spinner size="sm" />
                    <Text fontSize="sm" color="text.secondary">
                      Updating...
                    </Text>
                  </HStack>
                )}
              </HStack>
            </Flex>
          )}

          {/* Error State */}
          {hasError && (
            <Alert status="error" borderRadius="md">
              <AlertIcon />
              <Box>
                <Text fontWeight="bold">Search Error</Text>
                <Text fontSize="sm">
                  Unable to search movies. Please try again later.
                </Text>
              </Box>
            </Alert>
          )}

          {/* Loading State */}
          {isLoading && hasQuery && (
            <Center py={20}>
              <VStack spacing={4}>
                <Spinner size="xl" thickness="4px" />
                <Text color="text.secondary">Searching movies...</Text>
              </VStack>
            </Center>
          )}

          {/* No Results */}
          {showNoResults && (
            <Center py={20}>
              <VStack spacing={4} textAlign="center">
                <Text fontSize="xl" fontWeight="semibold">
                  No movies found
                </Text>
                <Text color="text.secondary" maxW="md">
                  We couldn&apos;t find any movies matching &quot;{query}&quot;.
                  Try adjusting your search terms or filters.
                </Text>
              </VStack>
            </Center>
          )}

          {/* Search Results with Infinite Scrolling */}
          {showResults && (
            <MovieGrid
              movies={movies}
              totalMovies={totalMovies}
              fetchedMoviesCount={fetchedMoviesCount}
              isLoading={isLoading}
              isFetchingNextPage={isFetchingNextPage}
              hasNextPage={hasNextPage}
              onLoadMore={handleLoadMore}
              error={error as Error | null}
              columns={{ base: 2, sm: 3, md: 4, lg: 5, xl: 6 }}
              source="search"
              emptyMessage={`No movies found for "${query}"`}
            />
          )}
        </VStack>
      </Container>
    </Box>
  );
}
