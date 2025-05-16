"use client";

import { Heading } from "@chakra-ui/react";
import MovieGrid from "@/components/home/MovieGrid";
import { memo } from "react";
import MovieBrowseLayout from "@/components/layout/MovieBrowseLayout";
import { useGenre, useParams } from "@/hooks";

// // Make the page dynamic to avoid prerendering issues
// export const dynamic = "force-dynamic";

// Memoize components to prevent unnecessary re-renders
const MemoizedMovieGrid = memo(MovieGrid);

// Genre page props interface
interface GenrePageProps {
  params: Promise<{ id: string }> | { id: string };
}

/**
 * GenrePage component - Displays movies filtered by genre
 *
 * Uses the shared MovieBrowseLayout for consistent UI with home page
 */
const GenrePage = ({ params: paramsPromise }: GenrePageProps) => {
  const params = useParams(paramsPromise);
  const genreId = params?.id ? Number(params.id) : 0;

  // Use the domain hook to access genre data
  const { genre } = useGenre(genreId);

  const genreTitle = (
    <Heading as="h1" marginY={5}>
      {genre?.name || "Genre"}
    </Heading>
  );

  return (
    <MovieBrowseLayout title={genreTitle}>
      <MemoizedMovieGrid
        columns={{ base: 3, sm: 3, md: 4, lg: 6 }}
        source="movie_listing"
        genre_id={genreId}
      />
    </MovieBrowseLayout>
  );
};

export default GenrePage;
