"use client";

import { Heading } from "@chakra-ui/react";
import MovieBrowseLayout from "@/components/layout/MovieBrowseLayout";
import MovieGrid from "@/components/home/MovieGrid";
import { memo } from "react";

// Memoize components for better performance
const MemoizedMovieGrid = memo(MovieGrid);

export default function WatchlistPage() {
  const title = (
    <Heading as="h1" marginY={5}>
      Your Watchlist
    </Heading>
  );

  return (
    <MovieBrowseLayout title={title}>
      <MemoizedMovieGrid
        columns={{ base: 3, sm: 3, md: 4, lg: 6 }}
        source="watchlist"
      />
    </MovieBrowseLayout>
  );
}
