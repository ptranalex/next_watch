import React, { useState, useEffect } from "react";
import { Box, Heading, Text, Flex, Spinner } from "@chakra-ui/react";
import { NextPage } from "next";
import Head from "next/head";
import { useRouter } from "next/router";
import { useQuery } from "@tanstack/react-query";
import { searchMovies } from "../services/movie-service";
import MovieGrid from "../components/movies/MovieGrid";
import useDebounce from "../hooks/useDebounce";
import SearchInput from "../components/SearchInput";

const SearchPage: NextPage = () => {
  const router = useRouter();
  const { q } = router.query;

  const [searchTerm, setSearchTerm] = useState((q as string) || "");
  const debouncedSearchTerm = useDebounce(searchTerm, 500);
  const [page, setPage] = useState(1);

  // Reset page when search term changes
  useEffect(() => {
    setPage(1);
  }, [debouncedSearchTerm]);

  // Update URL when search term changes
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

  // Fetch search results
  const { data, isLoading, error } = useQuery({
    queryKey: ["search", debouncedSearchTerm, page],
    queryFn: () => searchMovies(debouncedSearchTerm, page),
    enabled: !!debouncedSearchTerm && debouncedSearchTerm.length >= 2,
    keepPreviousData: true,
  });

  const handleLoadMore = () => {
    setPage((prevPage) => prevPage + 1);
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
                {isLoading ? (
                  <Flex justify="center" py={8}>
                    <Spinner size="xl" color="blue.400" />
                  </Flex>
                ) : (
                  <>
                    <Text mb={4} fontSize="lg">
                      {data?.total
                        ? `Found ${data.total} results for "${debouncedSearchTerm}"`
                        : `No results found for "${debouncedSearchTerm}"`}
                    </Text>

                    <MovieGrid
                      movies={data?.movies || []}
                      isLoading={isLoading}
                      hasMore={
                        !!data &&
                        data.page < Math.ceil(data.total / data.page_size)
                      }
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
