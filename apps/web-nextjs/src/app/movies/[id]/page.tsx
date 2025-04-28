"use client";

import { Suspense } from "react";
import {
  Box,
  Container,
  Heading,
  Spinner,
  Grid,
  GridItem,
} from "@chakra-ui/react";
import MovieDetailContent from "@/components/movies/detail/MovieDetailContent";
import MovieDetailSidebar from "@/components/movies/detail/MovieDetailSidebar";

interface MovieDetailPageProps {
  params: {
    id: string;
  };
}

export default function MovieDetailPage({ params }: MovieDetailPageProps) {
  const movieId = params.id;

  return (
    <Container maxW="container.xl" py={8}>
      <Heading as="h1" mb={6} size="xl">
        Movie Details
      </Heading>

      <Suspense
        fallback={
          <Box py={10} textAlign="center">
            <Spinner size="xl" />
          </Box>
        }
      >
        <Grid templateColumns={{ base: "1fr", lg: "3fr 1fr" }} gap={8}>
          <GridItem>
            <MovieDetailContent movieId={movieId} />
          </GridItem>

          <GridItem>
            <MovieDetailSidebar movieId={movieId} />
          </GridItem>
        </Grid>
      </Suspense>
    </Container>
  );
}
