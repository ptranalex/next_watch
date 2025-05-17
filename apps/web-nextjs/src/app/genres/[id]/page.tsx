"use client";

import { Heading } from "@chakra-ui/react";
import MovieGrid from "@/components/home/MovieGrid";
import { memo, useEffect } from "react";
import MovieBrowseLayout from "@/components/layout/MovieBrowseLayout";
import { useGenre, useParams } from "@/hooks";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("GenrePage");

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
  // Log component initialization
  logger.debug("GenrePage initializing");

  const params = useParams(paramsPromise);
  const genreId = params?.id ? Number(params.id) : 0;

  // Log the extracted genre ID
  useEffect(() => {
    logger.info(`Rendering genre page for genre ID: ${genreId}`);
  }, [genreId]);

  // Use the domain hook to access genre data
  const { genre } = useGenre(genreId);

  // Log when genre data changes
  useEffect(() => {
    if (genre) {
      logger.info(`Genre data loaded: ${genre.name} (ID: ${genreId})`);
    }
  }, [genre, genreId]);

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
