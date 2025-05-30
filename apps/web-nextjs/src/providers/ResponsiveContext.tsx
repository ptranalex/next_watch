"use client";

import React, {
  createContext,
  useContext,
  ReactNode,
  useEffect,
  useState,
} from "react";
import { useBreakpointValue, UseBreakpointOptions } from "@chakra-ui/react";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("ResponsiveContext");

interface ResponsiveContextType {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  hasTouchScreen: boolean;
  isHydrated: boolean;
}

const ResponsiveContext = createContext<ResponsiveContextType>({
  isMobile: false,
  isTablet: false,
  isDesktop: true,
  hasTouchScreen: false,
  isHydrated: false,
});

export const useResponsive = () => useContext(ResponsiveContext);

interface ResponsiveProviderProps {
  children: ReactNode;
}

/**
 * ResponsiveProvider
 * Provides responsive context values to all components
 * Centralizes breakpoint logic and device capability detection
 * Optimized for SSR to prevent layout shifting
 */
export const ResponsiveProvider: React.FC<ResponsiveProviderProps> = ({
  children,
}) => {
  // Track if we've hydrated the component on the client side
  const [isHydrated, setIsHydrated] = useState(false);

  // Options for breakpoint detection - ensure consistent SSR behavior
  const breakpointOptions: UseBreakpointOptions = {
    ssr: true,
    fallback: "lg", // Default to desktop during SSR for consistency
  };

  // Use breakpoint values to determine device type - hooks called unconditionally
  const mobileBreakpoint =
    useBreakpointValue({ base: true, sm: false }, breakpointOptions) ?? false;
  const tabletBreakpoint =
    useBreakpointValue({ sm: true, lg: false }, breakpointOptions) ?? false;
  const desktopBreakpoint =
    useBreakpointValue({ lg: true }, breakpointOptions) ?? true;

  // Apply hydration safety - only use computed values after hydration
  const isMobile = isHydrated ? mobileBreakpoint : false; // Default to false during SSR
  const isTablet = isHydrated ? tabletBreakpoint : false; // Default to false during SSR
  const isDesktop = isHydrated ? desktopBreakpoint : true; // Default to true during SSR

  // State for touch screen detection
  const [hasTouchScreen, setHasTouchScreen] = useState(false);

  // Set hydration state and detect touch after initial render
  useEffect(() => {
    // On client-side hydration, update the flag
    setIsHydrated(true);

    const detectTouch = () => {
      // Check for touch support using various browser APIs
      const hasTouchSupport =
        "ontouchstart" in window ||
        navigator.maxTouchPoints > 0 ||
        // @ts-expect-error - msMaxTouchPoints is not in standard TypeScript navigator type
        navigator.msMaxTouchPoints > 0 ||
        (window.matchMedia && window.matchMedia("(pointer: coarse)").matches);

      setHasTouchScreen(hasTouchSupport);
      logger.info(`Touch screen detected: ${hasTouchSupport}`);
    };

    detectTouch();

    // Log current state after hydration
    logger.info(
      `ResponsiveProvider hydrated: mobile=${isMobile}, tablet=${isTablet}, desktop=${isDesktop}`
    );
  }, [isMobile, isTablet, isDesktop]); // Re-run when breakpoints change

  const value = {
    isMobile,
    isTablet,
    isDesktop,
    hasTouchScreen,
    isHydrated,
  };

  return (
    <ResponsiveContext.Provider value={value}>
      {children}
    </ResponsiveContext.Provider>
  );
};

export default ResponsiveProvider;
