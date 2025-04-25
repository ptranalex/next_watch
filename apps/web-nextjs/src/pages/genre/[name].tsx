import React, { useState } from "react";
import { Box, Heading, Text, Flex, Select } from "@chakra-ui/react";
import { GetServerSideProps, NextPage } from "next";
import Head from "next/head";
import { useRouter } from "next/router";
import { dehydrate, QueryClient, useQuery } from "@tanstack/react-query";
import {
  getMoviesByGenre,
  getGenres,
  MoviesQueryParams,
  Genre,
} from "../../services/movie-service";
import MovieGrid from "../../components/movies/MovieGrid";

interface GenrePageProps {
  genreName: string;
  initialParams: MoviesQueryParams;
}

const GenrePage: NextPage<GenrePageProps> = ({ genreName, initialParams }) => {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const formattedGenreName =
    genreName.charAt(0).toUpperCase() + genreName.slice(1);

  // Fetch movies by genre using the movies endpoint with genre filter
  const { data, isLoading, error } = useQuery({
    queryKey: ["movies-by-genre", genreName, page, pageSize],
    queryFn: () => getMoviesByGenre(genreName, page, pageSize),
    keepPreviousData: true,
  });

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
    setPage((prevPage) => prevPage + 1);
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
            movies={data?.movies || []}
            isLoading={isLoading}
            hasMore={
              !!data && data.page < Math.ceil(data.total / data.page_size)
            }
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
    // Prefetch movies for initial render
    await queryClient.fetchQuery({
      queryKey: ["movies-by-genre", genreName, 1, pageSize],
      queryFn: () => getMoviesByGenre(genreName, 1, pageSize),
    });

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
