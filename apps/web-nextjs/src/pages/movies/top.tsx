import React from "react";
import { Box, Container, Heading } from "@chakra-ui/react";
import Head from "next/head";
import TopMoviesSection from "../../components/movies/TopMoviesSection";

const TopMoviesPage = () => {
  return (
    <>
      <Head>
        <title>Top Rated Movies | Next Watch</title>
        <meta
          name="description"
          content="Browse the top-rated movies by year or all-time based on IMDB ratings."
        />
      </Head>

      <Container maxW="container.xl" py={8}>
        <Heading as="h1" size="2xl" mb={8}>
          Top Rated Movies
        </Heading>

        <TopMoviesSection title="Top Movies" />
      </Container>
    </>
  );
};

export default TopMoviesPage;
