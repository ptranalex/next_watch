import React, { useState, useEffect } from "react";
import { Box, Heading, Flex, Select, Text, HStack } from "@chakra-ui/react";
import type { GetServerSideProps, NextPage } from "next";
import Head from "next/head";
import {
  dehydrate,
  QueryClient,
  useQuery,
  useQueryClient,
  useInfiniteQuery,
} from "@tanstack/react-query";
import {
  getMovies,
  Movie,
  MoviesQueryParams,
  MovieListResponse,
} from "../services/movie-service";
import MovieGrid from "../components/movies/MovieGrid";
import SearchInput from "../components/SearchInput";
import useDebounce from "../hooks/useDebounce";

interface HomePageProps {
  initialParams: MoviesQueryParams;
}

const HomePage: NextPage<HomePageProps> = ({ initialParams }) => {
  const [sortBy, setSortBy] = useState(
    initialParams.sortBy || "popularity.desc"
  );
  const [searchTerm, setSearchTerm] = useState("");
  const debouncedSearchTerm = useDebounce(searchTerm, 500);
  const queryClient = useQueryClient();

  // Use React Query for data fetching with infinite query
  const {
    data,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ["movies-infinite", { sortBy, search: debouncedSearchTerm }],
    queryFn: ({ pageParam = 1 }) =>
      getMovies({
        sortBy,
        search: debouncedSearchTerm,
        page: pageParam,
        pageSize: 20,
      }),
    getNextPageParam: (lastPage: MovieListResponse) => {
      // Calculate if there are more pages
      if (lastPage.page < Math.ceil(lastPage.total / lastPage.page_size)) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    initialData: debouncedSearchTerm
      ? undefined
      : () => {
          // Try to convert regular query data to infinite query format
          const data = queryClient.getQueryData<MovieListResponse>([
            "movies",
            { sortBy: initialParams.sortBy },
          ]);
          if (!data) return undefined;
          return {
            pages: [data],
            pageParams: [1],
          };
        },
  });

  // Extract all movies from all pages
  const allMovies = data?.pages.flatMap((page) => page.movies) || [];

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSortBy(e.target.value);
  };

  const handleSearch = (term: string) => {
    setSearchTerm(term);
  };

  const handleLoadMore = () => {
    fetchNextPage();
  };

  return (
    <>
      <Head>
        <title>Next Watch | Discover Movies</title>
        <meta
          name="description"
          content="Discover the latest and greatest movies"
        />
      </Head>

      <Box p={4}>
        <Flex
          justify="space-between"
          align={{ base: "start", md: "center" }}
          direction={{ base: "column", md: "row" }}
          gap={{ base: 4, md: 0 }}
          mb={6}
        >
          <Heading>
            {debouncedSearchTerm ? "Search Results" : "Popular Movies"}
          </Heading>

          <Flex
            gap={4}
            direction={{ base: "column", sm: "row" }}
            width={{ base: "100%", md: "auto" }}
          >
            <Box width={{ base: "100%", sm: "250px" }}>
              <SearchInput
                placeholder="Filter movies..."
                onSearch={handleSearch}
                initialValue={searchTerm}
              />
            </Box>

            <Select
              width={{ base: "100%", sm: "200px" }}
              value={sortBy}
              onChange={handleSortChange}
              bg="gray.700"
            >
              <option value="popularity.desc">Most Popular</option>
              <option value="vote_average.desc">Highest Rated</option>
              <option value="release_date.desc">Newest</option>
              <option value="release_date.asc">Oldest</option>
            </Select>
          </Flex>
        </Flex>

        {error ? (
          <Text color="red.400">
            Error loading movies: {(error as Error).message}
          </Text>
        ) : (
          <MovieGrid
            movies={allMovies}
            isLoading={isLoading || isFetchingNextPage}
            hasMore={hasNextPage}
            onLoadMore={handleLoadMore}
          />
        )}
      </Box>
    </>
  );
};

export const getServerSideProps: GetServerSideProps = async () => {
  const params: MoviesQueryParams = {
    sortBy: "popularity.desc",
    page: 1,
    pageSize: 20,
  };
  const queryClient = new QueryClient();

  try {
    // Prefetch movies for initial render
    await queryClient.fetchQuery({
      queryKey: ["movies", { sortBy: params.sortBy }],
      queryFn: () => getMovies(params),
    });

    return {
      props: {
        initialParams: params,
        dehydratedState: dehydrate(queryClient),
      },
    };
  } catch (error) {
    console.error("Error fetching movies:", error);
    return {
      props: {
        initialParams: params,
      },
    };
  }
};

export default HomePage;
