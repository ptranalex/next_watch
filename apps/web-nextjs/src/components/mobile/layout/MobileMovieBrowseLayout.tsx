import React, { ReactNode, useEffect } from "react";
import { Box } from "@chakra-ui/react";
import { useQueryClient } from "@tanstack/react-query";
import { GenreAPI, ActorAPI, MovieAPI } from "@/services/api";
import BottomActionBar from "@/components/mobile/common/BottomActionBar";
import { useMobileFilterButton } from "@/components/mobile/filters/FilterButton";
import { useMobileSortButton } from "@/components/mobile/filters/SortButton";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("MobileMovieBrowseLayout");

interface MobileMovieBrowseLayoutProps {
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
 * Mobile-optimized layout for movie browsing pages
 * Provides bottom action bar for key actions and improved touch targets
 * Supports same prefetching capabilities as the desktop version
 */
const MobileMovieBrowseLayout: React.FC<MobileMovieBrowseLayoutProps> = ({
  children,
  title,
  prefetchIds,
}) => {
  const queryClient = useQueryClient();
  const { filterAction, filterBottomSheet } = useMobileFilterButton();
  const { sortAction, sortBottomSheet } = useMobileSortButton();

  // Log component initialization
  logger.debug("Mobile layout initialized");

  // Prefetch data for smoother navigation between pages (same as desktop version)
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

  // Build the action array for the bottom bar
  const bottomActions = [sortAction, filterAction];

  return (
    <>
      <Box marginTop={5}>
        {title}
        <Box marginBottom={5}></Box>
      </Box>
      {children}

      {/* Add padding at the bottom to account for the action bar */}
      <Box height="80px" />

      {/* Render the bottom sheets */}
      {filterBottomSheet}
      {sortBottomSheet}
    </>
  );
};

export default MobileMovieBrowseLayout;
