"use client";

import React, { memo, Suspense, useEffect } from "react";
import NavBar from "../organisms/navigation/NavBar";
import SideBar from "../organisms/navigation/SideBar";
import { Box, Grid, GridItem, Show, Spinner } from "@chakra-ui/react";
import { useSyncFilterToUrl } from "@/hooks/filter/useSyncFilterToUrl";
import { useFilterResetOnRouteChange } from "@/hooks/filter/useFilterResetOnRouteChange";
import { useMovieFilterRehydration } from "@/hooks/filter/useMovieFilterRehydration";
import { createLogger } from "@/utils/logging";
import type { AppShellProps } from "./types";

// Create logger for this component
const logger = createLogger("AppShell");

// Memoize child components to prevent unnecessary re-renders
const MemoizedNavBar = memo(NavBar);
const MemoizedSideBar = memo(SideBar);

// Create a separate component for filter hooks
const FilterHooksProvider = () => {
  // Create specific logger for filter hooks
  const filterLogger = createLogger("FilterHooksProvider");

  useEffect(() => {
    filterLogger.debug("Initializing filter hooks");
  }, []);

  useFilterResetOnRouteChange();
  useMovieFilterRehydration();
  useSyncFilterToUrl();

  return null; // This component just runs hooks, doesn't render anything
};

// Create a component to wrap the main content with Suspense
const ContentWithSuspense = ({ children }: { children: React.ReactNode }) => {
  const suspenseLogger = createLogger("ContentWithSuspense");

  useEffect(() => {
    suspenseLogger.debug("Content suspense wrapper mounted");
  }, []);

  return (
    <Suspense
      fallback={
        <Box display="flex" justifyContent="center" py={10}>
          <Spinner size="xl" color="colors.primary" />
        </Box>
      }
    >
      {children}
    </Suspense>
  );
};

/**
 * AppShell component using shared AppShellProps
 *
 * Provides the main application layout structure with flexible header,
 * sidebar, footer, and content areas.
 *
 * @param children - Main content area
 * @param header - Header content (defaults to NavBar)
 * @param sidebar - Sidebar content (defaults to SideBar)
 * @param footer - Footer content (optional)
 * @param isSidebarOpen - Whether sidebar is open (responsive behavior)
 * @param onSidebarToggle - Callback for sidebar toggle
 */
function AppShell({
  children,
  header,
  sidebar,
  footer,
  isSidebarOpen,
  onSidebarToggle,
}: AppShellProps) {
  // Log app shell rendering
  useEffect(() => {
    logger.info("AppShell mounted - rendering main application layout");

    return () => {
      logger.debug("AppShell unmounting");
    };
  }, []);

  // Default components using existing implementation
  const defaultHeader = header || <MemoizedNavBar />;
  const defaultSidebar = sidebar || <MemoizedSideBar />;

  return (
    <>
      {/* Header area */}
      {defaultHeader}

      {/* Filter hooks provider */}
      <Suspense fallback={null}>
        <FilterHooksProvider />
      </Suspense>

      {/* Main layout container */}
      <Box px={{ base: 0, xl: 32 }} maxW="1600px" mx="auto" paddingX={5}>
        <Grid
          templateAreas={{
            base: `"main"`,
            lg: `"aside main"`,
          }}
          templateColumns={{ base: "1fr", lg: "200px 1fr" }}
        >
          {/* Sidebar area - responsive */}
          <Show above="lg">
            <GridItem area="aside" paddingRight={5}>
              {defaultSidebar}
            </GridItem>
          </Show>

          {/* Main content area */}
          <GridItem area="main">
            <ContentWithSuspense>{children}</ContentWithSuspense>
          </GridItem>
        </Grid>
      </Box>

      {/* Footer area */}
      {footer && <Box mt={8}>{footer}</Box>}
    </>
  );
}

// Export the memoized component to prevent unnecessary re-renders
export default memo(AppShell);
