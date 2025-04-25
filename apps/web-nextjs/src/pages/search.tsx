import React, { useState, useEffect } from "react";
import { Box, Heading, Text, Flex, Spinner } from "@chakra-ui/react";
import { NextPage } from "next";
import Head from "next/head";
import { useRouter } from "next/router";
import { useQuery, useInfiniteQuery } from "@tanstack/react-query";
import { searchMovies, MovieListResponse } from "../services/movie-service";
import MovieGrid from "../components/movies/MovieGrid";
import useDebounce from "../hooks/useDebounce";
import SearchInput from "../components/SearchInput";

const SearchPage: NextPage = () => {
  const router = useRouter();
  const { q } = router.query;

  const [searchTerm, setSearchTerm] = useState((q as string) || "");
  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  // Reset search state when term changes
  useEffect(() => {
    if (debouncedSearchTerm) {
      router.push(
        `/search?q=${encodeURIComponent(debouncedSearchTerm)}`,
        undefined,
        { shallow: true }
      );
    } else if (router.query.q) {
      router.push("/search", undefined, { shallow: true });
    }
  }, [debouncedSearchTerm, router]);

  // Fetch search results with infinite query
  const {
    data,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ["search-infinite", debouncedSearchTerm],
    queryFn: ({ pageParam = 1 }) =>
      searchMovies(debouncedSearchTerm, pageParam),
    getNextPageParam: (lastPage: MovieListResponse) => {
      if (lastPage.page < Math.ceil(lastPage.total / lastPage.page_size)) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    enabled: !!debouncedSearchTerm && debouncedSearchTerm.length >= 2,
  });

  // Extract all movies from all pages
  const allMovies = data?.pages.flatMap((page) => page.movies) || [];
  const totalResults = data?.pages[0]?.total || 0;

  const handleLoadMore = () => {
    fetchNextPage();
  };

  const handleSearch = (term: string) => {
    setSearchTerm(term);
  };

  return (
    <>
      <Head>
        <title>
          {debouncedSearchTerm
            ? `Search results for "${debouncedSearchTerm}" | Next Watch`
            : "Search Movies | Next Watch"}
        </title>
        <meta name="description" content="Search for your favorite movies" />
      </Head>

      <Box p={4}>
        <Heading mb={6}>Search Movies</Heading>

        <Box mb={8}>
          <SearchInput
            placeholder="Search for movies..."
            initialValue={searchTerm}
            onSearch={handleSearch}
            debounceTime={500}
          />
        </Box>

        {!debouncedSearchTerm && (
          <Flex justify="center" direction="column" align="center" py={12}>
            <Text color="gray.400" fontSize="lg" mb={4}>
              Enter a search term to find movies
            </Text>
          </Flex>
        )}

        {debouncedSearchTerm && debouncedSearchTerm.length < 2 && (
          <Flex justify="center" py={12}>
            <Text color="gray.400">
              Please enter at least 2 characters to search
            </Text>
          </Flex>
        )}

        {error ? (
          <Text color="red.400">
            Error searching movies: {(error as Error).message}
          </Text>
        ) : (
          <>
            {debouncedSearchTerm && debouncedSearchTerm.length >= 2 && (
              <Box mb={4}>
                {isLoading && !isFetchingNextPage ? (
                  <Flex justify="center" py={8}>
                    <Spinner size="xl" color="blue.400" />
                  </Flex>
                ) : (
                  <>
                    <Text mb={4} fontSize="lg">
                      {totalResults
                        ? `Found ${totalResults} results for "${debouncedSearchTerm}"`
                        : `No results found for "${debouncedSearchTerm}"`}
                    </Text>

                    <MovieGrid
                      movies={allMovies}
                      isLoading={isLoading || isFetchingNextPage}
                      hasMore={hasNextPage}
                      onLoadMore={handleLoadMore}
                    />
                  </>
                )}
              </Box>
            )}
          </>
        )}
      </Box>
    </>
  );
};

export default SearchPage;
