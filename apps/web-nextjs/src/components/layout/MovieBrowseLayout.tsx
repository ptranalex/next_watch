"use client";

import SortSelector from "@/components/layout/SortSelector";
import FilterButton from "@/components/home/FilterButton";
import { Box, Flex } from "@chakra-ui/react";
import React, { memo, ReactNode, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { MovieAPI, GenreAPI, ActorAPI } from "@/services/api";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("MovieBrowseLayout");

// Memoize components to prevent unnecessary re-renders
const MemoizedSortSelector = memo(SortSelector);
const MemoizedFilterButton = memo(FilterButton);

interface MovieBrowseLayoutProps {
  children: ReactNode;
  title: ReactNode;
  rightHeader?: ReactNode;
  prefetchIds?: {
    genreIds?: number[];
    actorIds?: number[];
    movieIds?: number[];
  };
}

/**
 * Shared layout for movie browsing pages
 * Provides consistent structure for home, genre, actor, and other browsing views
 * Includes prefetching capability for smoother navigation
 */
const MovieBrowseLayout: React.FC<MovieBrowseLayoutProps> = ({
  children,
  title,
  rightHeader,
  prefetchIds,
}) => {
  const queryClient = useQueryClient();

  // Prefetch data for smoother navigation between pages
  useEffect(() => {
    if (!prefetchIds) return;

    // Prefetch genre data
    if (prefetchIds.genreIds?.length) {
      prefetchIds.genreIds.forEach((id) => {
        queryClient.prefetchQuery({
          queryKey: ["genre", id],
          queryFn: () => GenreAPI.getById(id),
        });
      });
    }

    // Prefetch actor data
    if (prefetchIds.actorIds?.length) {
      prefetchIds.actorIds.forEach((id) => {
        queryClient.prefetchQuery({
          queryKey: ["actor", id],
          queryFn: () => ActorAPI.getById(id),
        });
      });
    }

    // Prefetch movie data
    if (prefetchIds.movieIds?.length) {
      prefetchIds.movieIds.forEach((id) => {
        queryClient.prefetchQuery({
          queryKey: ["movie", id],
          queryFn: () => MovieAPI.getById(id),
        });
      });
    }
  }, [prefetchIds, queryClient]);

  return (
    <>
      <Box marginTop={5}>
        {title}
        <Box marginBottom={5}>
          {rightHeader || (
            <Flex alignItems="center">
              <MemoizedSortSelector />
              <MemoizedFilterButton />
            </Flex>
          )}
        </Box>
      </Box>
      {children}
    </>
  );
};

export default MovieBrowseLayout;
