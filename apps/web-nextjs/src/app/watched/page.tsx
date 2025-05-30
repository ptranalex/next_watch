"use client";

import { memo } from "react";
import { WatchedPage } from "@/components/features/movies/watched";
import { createLogger } from "@/utils/logging";

// Create logger for this route
const logger = createLogger("WatchedPageRoute");

/**
 * Watched Page Route - /watched
 *
 * Route-level component that delegates rendering to the WatchedPage feature component.
 *
 * This follows the architecture pattern where route files only handle
 * parameter parsing (none needed here) and delegate business logic to feature components.
 */
const WatchedPageRoute = memo(() => {
  // Log route initialization
  logger.debug("WatchedPageRoute initializing");

  // Delegate to the feature component
  return <WatchedPage />;
});

WatchedPageRoute.displayName = "WatchedPageRoute";

export default WatchedPageRoute;
