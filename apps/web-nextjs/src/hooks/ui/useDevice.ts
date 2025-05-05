import { useBreakpointValue } from "@chakra-ui/react";

interface DeviceInfo {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isLargeScreen: boolean;
}

/**
 * Centralized hook for responsive device detection
 * Uses SSR-friendly defaults to prevent layout shifts
 */
export const useDevice = (): DeviceInfo => {
  // Configure with SSR true for consistent initial rendering
  const breakpoint = useBreakpointValue(
    {
      base: "mobile",
      sm: "mobile",
      md: "tablet",
      lg: "desktop",
      xl: "largeScreen",
    },
    {
      // Use SSR-friendly default (mobile-first approach)
      ssr: true,
      // Force fallback to avoid React 18 hydration warnings
      fallback: "mobile",
    }
  );

  return {
    isMobile: breakpoint === "mobile",
    isTablet: breakpoint === "tablet",
    isDesktop: breakpoint === "desktop" || breakpoint === "largeScreen",
    isLargeScreen: breakpoint === "largeScreen",
  };
};

// Export breakpoint values for use in other contexts
export const BREAKPOINTS = {
  mobile: "480px",
  tablet: "768px",
  desktop: "992px",
  largeScreen: "1280px",
};
