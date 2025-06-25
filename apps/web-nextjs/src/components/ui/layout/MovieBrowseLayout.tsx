"use client";

import SortSelector from "@/components/ui/molecules/SortSelector";
import { FilterButton } from "@/components/features/movies/filter";
import { Box, Flex } from "@chakra-ui/react";
import React, { memo, ReactNode, useEffect } from "react";
import { useResponsive } from "@/providers";
import { createLogger } from "@/utils/logging";
import { MobileMovieBrowseLayout } from "@/components/mobile/core/layout/movie-browse";
import type { BrowseLayoutProps } from "./types";

// Create logger for this component
const logger = createLogger("MovieBrowseLayout");

// Memoize components to prevent unnecessary re-renders
const MemoizedSortSelector = memo(SortSelector);
const MemoizedFilterButton = memo(FilterButton);

/**
 * MovieBrowseLayout Props
 *
 * Extends the shared BrowseLayoutProps with movie-specific functionality
 */
interface MovieBrowseLayoutProps
  extends Omit<BrowseLayoutProps, "title" | "content"> {
  children: ReactNode; // Map content to children for React conventions
  title: ReactNode; // Keep as ReactNode for flexibility
  rightHeader?: ReactNode; // Legacy prop for backward compatibility
}

/**
 * Shared layout for movie browsing pages
 *
 * Provides consistent structure for home, genre, actor, and other browsing views
 * using the shared BrowseLayoutProps pattern.
 *
 * @param children - Main content area (maps to BrowseLayoutProps.content)
 * @param title - Page title (from BrowseLayoutProps)
 * @param search - Search component (from BrowseLayoutProps)
 * @param sort - Sort component (from BrowseLayoutProps, defaults to SortSelector)
 * @param filters - Filter component (from BrowseLayoutProps, defaults to FilterButton)
 * @param sidebar - Sidebar content (from BrowseLayoutProps)
 * @param pagination - Pagination component (from BrowseLayoutProps)
 * @param actions - Action buttons (from BrowseLayoutProps)
 * @param rightHeader - Legacy prop for backward compatibility
 */
const MovieBrowseLayout: React.FC<MovieBrowseLayoutProps> = ({
  children,
  title,
  search,
  sort,
  filters,
  sidebar,
  pagination,
  actions,
  rightHeader, // Legacy support
}) => {
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

  // Default components following BrowseLayoutProps pattern
  const defaultSort = sort || <MemoizedSortSelector />;
  const defaultFilters = filters || <MemoizedFilterButton />;

  // Combine legacy rightHeader with new pattern
  const headerControls = rightHeader || (
    <Flex alignItems="center">
      {search}
      {defaultSort}
      <Box marginLeft={3}>{defaultFilters}</Box>
    </Flex>
  );

  // SSR-safe default layout: always render desktop layout during SSR
  // Only switch to mobile layout after hydration if on mobile
  if (!isHydrated || !isMobile) {
    // Tablet & desktop layout following BrowseLayoutProps structure
    return (
      <Box w="100%" className="desktop-movie-browse-layout">
        <Box marginY={5}>
          {title}
          <Box marginBottom={5}>{headerControls}</Box>
        </Box>

        {/* Main content area */}
        <Flex>
          {sidebar && <Box marginRight={5}>{sidebar}</Box>}
          <Box flex="1">{children}</Box>
        </Flex>

        {/* Pagination area */}
        {pagination && <Box marginTop={5}>{pagination}</Box>}

        {/* Actions area */}
        {actions && <Box marginTop={3}>{actions}</Box>}
      </Box>
    );
  }

  // Only render mobile layout after hydration is complete and we've confirmed mobile device
  // Use the specialized MobileMovieBrowseLayout for optimized mobile experience
  return (
    <MobileMovieBrowseLayout title={title}>{children}</MobileMovieBrowseLayout>
  );
};

export default MovieBrowseLayout;
