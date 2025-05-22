import React, { ReactNode, useEffect } from "react";
import { Box, useDisclosure } from "@chakra-ui/react";
import { useQueryClient } from "@tanstack/react-query";
import { GenreAPI, ActorAPI, MovieAPI } from "@/services/api";
import { createLogger } from "@/utils/logging";
import useMovieFilterStore from "@/store/movieFilterStore";
import MovieFilterBottomSheet from "@/components/mobile/features/filters/MovieFilterBottomSheet";
import SortOptionsBottomSheet from "@/components/mobile/features/filters/SortOptionsBottomSheet";
import { ActionPill } from "@/components/mobile/ui/action-pill";
import { HiSortAscending } from "react-icons/hi";
import { HiAdjustmentsHorizontal } from "react-icons/hi2";

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
  const { filters } = useMovieFilterStore();

  // Use disclosures directly for bottom sheets
  const {
    isOpen: isFilterOpen,
    onOpen: onFilterOpen,
    onClose: onFilterClose,
  } = useDisclosure();

  const {
    isOpen: isSortOpen,
    onOpen: onSortOpen,
    onClose: onSortClose,
  } = useDisclosure();

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

  // Helper function to get display name for current sort order
  const getSortDisplayName = () => {
    const { sortOrder, sortDesc } = filters;

    // Map sort field to human readable name
    let fieldName = "Release date";
    if (sortOrder === "title") fieldName = "Name";
    else if (sortOrder === "imdb_rating") fieldName = "IMDB";
    else if (sortOrder === "rotten_tomatoes_rating") fieldName = "RT";
    else if (sortOrder === "metacritic_rating") fieldName = "Meta";
    else if (sortOrder === "vote_count") fieldName = "Popular";

    return `${fieldName} ${sortDesc ? "↓" : "↑"}`;
  };

  // Helper function to get display name for active filters count
  const getFilterCount = () => {
    let count = 0;
    if (filters.imdb_rating !== undefined) count++;
    if (filters.rotten_tomatoes_rating !== undefined) count++;
    if (filters.metacritic_rating !== undefined) count++;
    if (filters.year !== undefined) count++;

    return count > 0 ? `${count}` : "";
  };

  const handleSortClick = () => {
    logger.info("Opening mobile sort options");

    // Add haptic feedback
    if (window.navigator && "vibrate" in window.navigator) {
      try {
        window.navigator.vibrate(30);
      } catch (e) {
        logger.warn("Vibration not supported", e);
      }
    }

    onSortOpen();
  };

  const handleFilterClick = () => {
    logger.info("Opening mobile filter options");

    // Add haptic feedback
    if (window.navigator && "vibrate" in window.navigator) {
      try {
        window.navigator.vibrate(30);
      } catch (e) {
        logger.warn("Vibration not supported", e);
      }
    }

    onFilterOpen();
  };

  return (
    <>
      <Box marginTop={5}>
        {title}
        <Box marginBottom={5}></Box>
      </Box>
      {children}

      {/* Add padding at the bottom to account for the sticky buttons */}
      <Box height="80px" />

      {/* Use the modular ActionPill component */}
      <ActionPill
        actions={[
          {
            id: "sort",
            label: getSortDisplayName(),
            icon: <HiSortAscending size={18} />,
            onClick: handleSortClick,
          },
          {
            id: "filter",
            label: "Filter",
            badge: getFilterCount(),
            icon: <HiAdjustmentsHorizontal size={18} />,
            onClick: handleFilterClick,
          },
        ]}
      />

      {/* Render the bottom sheets directly */}
      <MovieFilterBottomSheet isOpen={isFilterOpen} onClose={onFilterClose} />
      <SortOptionsBottomSheet isOpen={isSortOpen} onClose={onSortClose} />
    </>
  );
};

export default MobileMovieBrowseLayout;
