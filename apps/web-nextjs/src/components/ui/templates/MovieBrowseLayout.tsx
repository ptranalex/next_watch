"use client";

import SortSelector from "@/components/ui/molecules/SortSelector";
import { FilterButton } from "@/components/features/movies/filter";
import { Box, Flex } from "@chakra-ui/react";
import React, { memo, ReactNode, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { MovieAPI, GenreAPI, ActorAPI } from "@/services/api";
import { useResponsive } from "@/providers";
import { createLogger } from "@/utils/logging";
import { MobileMovieBrowseLayout } from "@/components/mobile/core/layout/movie-browse";

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
 * Mobile-first design with device-specific layout adjustments
 * SSR-safe: always renders desktop layout during SSR for minimal layout shifts
 */
const MovieBrowseLayout: React.FC<MovieBrowseLayoutProps> = ({
  children,
  title,
  rightHeader,
  prefetchIds,
}) => {
  const queryClient = useQueryClient();
  const { isMobile, isTablet, isHydrated } = useResponsive();

  // Log device type for debugging
  useEffect(() => {
    if (isHydrated) {
      logger.debug(
        `MovieBrowseLayout rendering for ${
          isMobile ? "mobile" : isTablet ? "tablet" : "desktop"
        } view (hydrated)`
      );
    }
  }, [isMobile, isTablet, isHydrated]);

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

  // SSR-safe default layout: always render desktop layout during SSR
  // Only switch to mobile layout after hydration if on mobile
  if (!isHydrated || !isMobile) {
    // Tablet & desktop layout
    return (
      <Box w="100%" className="desktop-movie-browse-layout">
        <Box marginY={5}>
          {title}
          <Box marginBottom={5}>
            {rightHeader || (
              <Flex alignItems="center">
                <MemoizedSortSelector />
                <Box marginLeft={3}>
                  <MemoizedFilterButton />
                </Box>
              </Flex>
            )}
          </Box>
        </Box>
        {children}
      </Box>
    );
  }

  // Only render mobile layout after hydration is complete and we've confirmed mobile device
  // Use the specialized MobileMovieBrowseLayout for optimized mobile experience
  return (
    <MobileMovieBrowseLayout title={title} prefetchIds={prefetchIds}>
      {children}
    </MobileMovieBrowseLayout>
  );
};

export default MovieBrowseLayout;
