import React, { useEffect, memo } from "react";
import { createLogger } from "@/utils/logging";
import { useResponsive } from "@/context/ResponsiveContext";
import DesktopMovieDetailView from "./DesktopMovieDetailView";
import MobileMovieDetailView from "@/components/mobile/movieDetails/MobileMovieDetailView";
import { MovieDetailViewProps } from "./types";

// Create logger for this component
const logger = createLogger("MovieDetailView");

/**
 * The main component for displaying detailed movie information
 * Selects between mobile and desktop layouts based on device type
 * SSR-safe: always renders desktop layout during SSR for minimal layout shifts
 */
const MovieDetailView: React.FC<MovieDetailViewProps> = (props) => {
  const { isMobile, isHydrated } = useResponsive();

  // Log which layout is being rendered
  useEffect(() => {
    if (isHydrated) {
      logger.info(
        `MovieDetailView choosing ${isMobile ? "mobile" : "desktop"} layout`
      );
    }
  }, [isMobile, isHydrated]);

  // SSR-safe default layout: always render desktop layout during SSR
  // Only switch to mobile layout after hydration if on mobile
  if (!isHydrated || !isMobile) {
    return <DesktopMovieDetailView {...props} />;
  }

  // Only render mobile layout after hydration is complete and we've confirmed mobile device
  return <MobileMovieDetailView {...props} />;
};

export default memo(MovieDetailView);
