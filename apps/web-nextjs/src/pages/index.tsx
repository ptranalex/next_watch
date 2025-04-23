import React, { useState } from "react";
import { Box, Heading, Flex, Select, Text } from "@chakra-ui/react";
import type { GetServerSideProps, NextPage } from "next";
import Head from "next/head";
import {
  dehydrate,
  QueryClient,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { getMovies, Movie, MoviesQueryParams } from "../services/movie-service";
import MovieGrid from "../components/movies/MovieGrid";

interface HomePageProps {
  initialParams: MoviesQueryParams;
}

const HomePage: NextPage<HomePageProps> = ({ initialParams }) => {
  const [sortBy, setSortBy] = useState(
    initialParams.sortBy || "popularity.desc"
  );
  const queryClient = useQueryClient();

  // Use React Query for data fetching
  const { data, isLoading, error } = useQuery({
    queryKey: ["movies", { sortBy }],
    queryFn: () => getMovies({ sortBy }),
    initialData: queryClient.getQueryData([
      "movies",
      { sortBy: initialParams.sortBy },
    ]),
  });

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSortBy(e.target.value);
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
        <Flex justify="space-between" align="center" mb={6}>
          <Heading>Popular Movies</Heading>

          <Select
            width="200px"
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

        {error ? (
          <Text color="red.400">
            Error loading movies: {(error as Error).message}
          </Text>
        ) : (
          <MovieGrid movies={data?.movies || []} isLoading={isLoading} />
        )}
      </Box>
    </>
  );
};

export const getServerSideProps: GetServerSideProps = async () => {
  const params: MoviesQueryParams = { sortBy: "popularity.desc" };
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
