"use client";

import { memo } from "react";
import { Heading } from "@chakra-ui/react";
import MovieGrid from "@/components/home/MovieGrid";
import MovieBrowseLayout from "@/components/layout/MovieBrowseLayout";

// Make the page dynamic to avoid prerendering issues
export const dynamic = "force-dynamic";

// Memoize components
const MemoizedMovieGrid = memo(MovieGrid);

/**
 * HomePage component - Entry point for the application's main page
 *
 * Uses the shared MovieBrowseLayout for consistent UI with genre pages
 */
const HomePage: React.FC = () => {
  const title = (
    <Heading as="h1" marginY={5}>
      All Movies
    </Heading>
  );

  return (
    <MovieBrowseLayout title={title}>
      <MemoizedMovieGrid
        columns={{ base: 3, sm: 3, md: 4, lg: 6 }}
        source="movie_listing"
      />
    </MovieBrowseLayout>
  );
};

export default HomePage;
