import React, { memo, useEffect } from "react";
import { Box, Flex } from "@chakra-ui/react";
import { useResponsive } from "@/providers";
import { createLogger } from "@/utils/logging";

const logger = createLogger("PageLayout");

interface PageLayoutProps {
  /** Page title element */
  title: React.ReactNode;
  /** Main page content */
  children: React.ReactNode;
  /** Optional sidebar content */
  sidebar?: React.ReactNode;
  /** Optional actions area (e.g., pagination, buttons) */
  actions?: React.ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Maximum width constraint */
  maxWidth?: string;
}

/**
 * PageLayout - Generic page layout component
 *
 * Provides basic page structure without domain-specific elements:
 * - Page title
 * - Main content area
 * - Optional sidebar
 * - Optional actions area
 * - Responsive behavior
 *
 * Unlike MovieBrowseLayout, this doesn't include:
 * - Sort selectors
 * - Filter buttons
 * - Browse-specific functionality
 *
 * Use this for:
 * - Error states
 * - Settings pages
 * - Profile pages
 * - Generic content pages
 */
const PageLayout = memo(
  ({
    title,
    children,
    sidebar,
    actions,
    className = "",
    maxWidth = "none",
  }: PageLayoutProps) => {
    const { isMobile, isTablet, isHydrated } = useResponsive();

    // Log device type for debugging
    useEffect(() => {
      if (isHydrated) {
        logger.debug(
          `PageLayout rendering for ${
            isMobile ? "mobile" : isTablet ? "tablet" : "desktop"
          } view (hydrated)`
        );
      }
    }, [isMobile, isTablet, isHydrated]);

    // SSR-safe default layout: always render desktop layout during SSR
    // Only switch to mobile layout after hydration if on mobile
    if (!isHydrated || !isMobile) {
      // Desktop & tablet layout
      return (
        <Box
          w="100%"
          maxWidth={maxWidth}
          mx="auto"
          className={`desktop-page-layout ${className}`}
        >
          {/* Page header with title */}
          <Box marginY={5}>{title}</Box>

          {/* Main content area */}
          <Flex gap={5}>
            {sidebar && (
              <Box
                minWidth="200px"
                maxWidth="300px"
                display={{ base: "none", md: "block" }}
              >
                {sidebar}
              </Box>
            )}

            <Box flex="1">{children}</Box>
          </Flex>

          {/* Actions area (pagination, buttons, etc.) */}
          {actions && <Box marginTop={6}>{actions}</Box>}
        </Box>
      );
    }

    // Mobile layout - simplified structure
    return (
      <Box w="100%" className={`mobile-page-layout ${className}`} paddingX={4}>
        {/* Mobile title */}
        <Box marginY={4}>{title}</Box>

        {/* Mobile sidebar (if provided, render above content) */}
        {sidebar && <Box marginBottom={4}>{sidebar}</Box>}

        {/* Main content */}
        <Box>{children}</Box>

        {/* Mobile actions */}
        {actions && (
          <Box marginTop={4} marginBottom={4}>
            {actions}
          </Box>
        )}
      </Box>
    );
  }
);

PageLayout.displayName = "PageLayout";

export default PageLayout;
