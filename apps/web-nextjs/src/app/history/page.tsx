"use client";

import { Heading } from "@chakra-ui/react";
import MovieBrowseLayout from "@/components/ui/templates/MovieBrowseLayout";
import MovieGrid from "@/components/features/movies/grid/MovieGrid";
import { memo } from "react";

// Memoize components for better performance
const MemoizedMovieGrid = memo(MovieGrid);

export default function HistoryPage() {
  const title = (
    <Heading as="h1" marginY={5}>
      Watch History
    </Heading>
  );

  return (
    <MovieBrowseLayout title={title}>
      <MemoizedMovieGrid
        columns={{ base: 3, sm: 3, md: 4, lg: 6 }}
        source="watched"
      />
    </MovieBrowseLayout>
  );
}
