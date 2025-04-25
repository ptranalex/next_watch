import React, { useState, useEffect } from "react";
import { Box, Heading, Text, Flex, Select } from "@chakra-ui/react";
import { GetServerSideProps, NextPage } from "next";
import Head from "next/head";
import { useRouter } from "next/router";
import {
  dehydrate,
  QueryClient,
  useQuery,
  useInfiniteQuery,
} from "@tanstack/react-query";
import {
  getMoviesByGenre,
  getGenres,
  MoviesQueryParams,
  Genre,
  MovieListResponse,
} from "../../services/movie-service";
import MovieGrid from "../../components/movies/MovieGrid";

interface GenrePageProps {
  genreName: string;
  initialParams: MoviesQueryParams;
}

const GenrePage: NextPage<GenrePageProps> = ({ genreName, initialParams }) => {
  const router = useRouter();
  const [pageSize] = useState(20);
  const formattedGenreName =
    genreName.charAt(0).toUpperCase() + genreName.slice(1);

  // Fetch movies by genre using infinite query
  const {
    data,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ["movies-by-genre-infinite", genreName, pageSize],
    queryFn: ({ pageParam = 1 }) =>
      getMoviesByGenre(genreName, pageParam, pageSize),
    getNextPageParam: (lastPage: MovieListResponse) => {
      if (lastPage.page < Math.ceil(lastPage.total / lastPage.page_size)) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
  });

  // Extract all movies from all pages
  const allMovies = data?.pages.flatMap((page) => page.movies) || [];

  // Fetch all genres for validation and dropdown
  const { data: genresData } = useQuery({
    queryKey: ["genres"],
    queryFn: getGenres,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Check if genre exists
  const genreExists = genresData?.some(
    (genre: Genre) => genre.name.toLowerCase() === genreName.toLowerCase()
  );

  const handleLoadMore = () => {
    console.log(`Attempting to load more ${genreName} movies...`);
    if (!isFetchingNextPage) {
      fetchNextPage();
    }
  };

  // Handle invalid genre
  if (genresData && !genreExists && !isLoading) {
    return (
      <Box p={8} textAlign="center">
        <Heading size="lg" mb={4}>
          Genre Not Found
        </Heading>
        <Text mb={6}>
          The genre "{formattedGenreName}" does not exist or contains no movies.
        </Text>
      </Box>
    );
  }

  return (
    <>
      <Head>
        <title>{formattedGenreName} Movies | Next Watch</title>
        <meta
          name="description"
          content={`Browse the best ${formattedGenreName} movies`}
        />
      </Head>

      <Box p={4}>
        <Flex justify="space-between" align="center" mb={6}>
          <Heading>{formattedGenreName} Movies</Heading>

          <Select
            width="200px"
            bg="gray.700"
            onChange={(e) =>
              router.push(`/genre/${e.target.value.toLowerCase()}`)
            }
            value={genreName}
          >
            {genresData?.map((genre: Genre) => (
              <option key={genre.id} value={genre.name.toLowerCase()}>
                {genre.name}
              </option>
            ))}
          </Select>
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

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { name } = context.params || {};
  const genreName = String(name).toLowerCase();
  const queryClient = new QueryClient();
  const pageSize = 20; // Match the pageSize used in the component

  try {
    // Prefetch first page of movies for initial render using infinite query structure
    const moviesData = await getMoviesByGenre(genreName, 1, pageSize);

    // Manually set the infinite query data structure
    queryClient.setQueryData(
      ["movies-by-genre-infinite", genreName, pageSize],
      {
        pages: [moviesData],
        pageParams: [1],
      }
    );

    // Prefetch genres for dropdown
    await queryClient.fetchQuery({
      queryKey: ["genres"],
      queryFn: getGenres,
    });

    return {
      props: {
        genreName,
        initialParams: { genre: genreName, page: 1, pageSize },
        dehydratedState: dehydrate(queryClient),
      },
    };
  } catch (error) {
    console.error(`Error fetching genre ${genreName}:`, error);
    return {
      props: {
        genreName,
        initialParams: { genre: genreName, page: 1, pageSize },
      },
    };
  }
};

export default GenrePage;
