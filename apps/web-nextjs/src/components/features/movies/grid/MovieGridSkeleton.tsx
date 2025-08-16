"use client";

import {
  MovieCardContainer,
  MovieCardSkeleton,
} from "@/components/features/movies/card";
import { SimpleGrid } from "@chakra-ui/react";
import React, { memo } from "react";

// Column breakpoints type (matches MovieGrid)
type ColumnBreakpoints =
  | {
      [key in "base" | "xs" | "sm" | "md" | "lg" | "xl"]?: number;
    }
  | number
  | number[];

interface MovieGridSkeletonProps {
  /** Number of skeleton cards to display */
  count?: number;
  /** Grid column configuration (matches MovieGrid columns prop) */
  columns: ColumnBreakpoints;
  /** Grid spacing */
  spacing?: number;
}

/**
 * MovieGridSkeleton - Shared skeleton component for consistent movie grid loading states
 *
 * Creates a grid of MovieCardSkeleton components that match the real MovieGrid layout.
 * Used by:
 * - MovieBrowseLayoutSkeleton
 * - GenrePageSkeleton
 * - ActorPageSkeleton
 * - TopMoviesPageSkeleton
 * - And other grid-based movie displays
 *
 * Automatically respects the current color mode (light/dark theme).
 */
const MovieGridSkeleton = memo(
  ({ count = 12, columns, spacing = 4 }: MovieGridSkeletonProps) => {
    const skeletonsArray = Array.from({ length: count }, (_, i) => i + 1);

    return (
      <SimpleGrid columns={columns} spacing={spacing}>
        {skeletonsArray.map((key) => (
          <MovieCardContainer key={`movie-skeleton-${key}`}>
            <MovieCardSkeleton />
          </MovieCardContainer>
        ))}
      </SimpleGrid>
    );
  }
);

MovieGridSkeleton.displayName = "MovieGridSkeleton";

export default MovieGridSkeleton;
