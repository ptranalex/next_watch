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
  genreId: number;
  initialParams: MoviesQueryParams;
}

const GenrePage: NextPage<GenrePageProps> = ({ genreId, initialParams }) => {
  const router = useRouter();
  const [pageSize] = useState(20);

  // Fetch all genres for name lookup and dropdown
  const { data: genres, isLoading: isLoadingGenres } = useQuery({
    queryKey: ["genres"],
    queryFn: getGenres,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Find the current genre from the genres list
  const currentGenre = genres?.find((g) => g.id === genreId);
  const genreName = currentGenre?.name || "";

  // Fetch movies by genre using infinite query
  const {
    data,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ["movies-by-genre-infinite", genreId, pageSize],
    queryFn: ({ pageParam = 1 }) =>
      getMoviesByGenre(genreId, pageParam, pageSize),
    getNextPageParam: (lastPage: MovieListResponse) => {
      if (lastPage.page < Math.ceil(lastPage.total / lastPage.page_size)) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
    enabled: Boolean(genreId),
  });

  // Extract all movies from all pages
  const allMovies = data?.pages.flatMap((page) => page.movies) || [];

  // Log info for debugging
  useEffect(() => {
    if (data?.pages?.length) {
      console.log(
        `Genre ${genreId}: Loaded ${allMovies.length} movies across ${data.pages.length} pages`
      );
    }
  }, [data?.pages?.length, allMovies.length, genreId]);

  const handleLoadMore = () => {
    console.log(`Attempting to load more movies for genre ID ${genreId}...`);
    if (!isFetchingNextPage) {
      fetchNextPage();
    }
  };

  const handleGenreChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedGenreId = parseInt(e.target.value, 10);
    router.push(`/genre/${selectedGenreId}`);
  };

  // Handle invalid genre
  if (genres && !currentGenre && !isLoadingGenres) {
    return (
      <Box p={8} textAlign="center">
        <Heading size="lg" mb={4}>
          Genre Not Found
        </Heading>
        <Text mb={6}>
          The genre with ID {genreId} does not exist or contains no movies.
        </Text>
      </Box>
    );
  }

  // Handle loading state
  if (isLoadingGenres) {
    return (
      <Box p={8} textAlign="center">
        <Text>Loading genre information...</Text>
      </Box>
    );
  }

  return (
    <>
      <Head>
        <title>{genreName} Movies | Next Watch</title>
        <meta
          name="description"
          content={`Browse the best ${genreName} movies`}
        />
      </Head>

      <Box p={4}>
        <Flex justify="space-between" align="center" mb={6}>
          <Heading>{genreName} Movies</Heading>

          <Select
            width="200px"
            bg="gray.700"
            onChange={handleGenreChange}
            value={genreId.toString()}
          >
            {genres?.map((genre: Genre) => (
              <option key={genre.id} value={genre.id.toString()}>
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
  const { id } = context.params || {};
  const genreId = parseInt(String(id), 10);

  // Return 404 for invalid IDs
  if (isNaN(genreId)) {
    return {
      notFound: true,
    };
  }

  const queryClient = new QueryClient();
  const pageSize = 20; // Match the pageSize used in the component

  try {
    // Prefetch genres for dropdown and name lookup
    await queryClient.fetchQuery({
      queryKey: ["genres"],
      queryFn: getGenres,
    });

    // Prefetch first page of movies for initial render
    try {
      const moviesData = await getMoviesByGenre(genreId, 1, pageSize);

      // Manually set the infinite query data structure
      queryClient.setQueryData(
        ["movies-by-genre-infinite", genreId, pageSize],
        {
          pages: [moviesData],
          pageParams: [1],
        }
      );
    } catch (err) {
      console.error(`Error fetching movies for genre ${genreId}:`, err);
      // Continue despite movie fetch error - the page will handle it
    }

    return {
      props: {
        genreId,
        initialParams: { genre_id: genreId, page: 1, pageSize },
        dehydratedState: dehydrate(queryClient),
      },
    };
  } catch (error) {
    console.error(`Error in getServerSideProps for genre ${genreId}:`, error);
    return {
      props: {
        genreId,
        initialParams: { genre_id: genreId, page: 1, pageSize },
      },
    };
  }
};

export default GenrePage;
