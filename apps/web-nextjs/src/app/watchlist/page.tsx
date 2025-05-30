"use client";

import { memo } from "react";
import { WatchlistPage } from "@/components/features/movies/watchlist";
import { createLogger } from "@/utils/logging";

// Create logger for this route
const logger = createLogger("WatchlistPageRoute");

/**
 * Watchlist Page Route - /watchlist
 *
 * Route-level component that delegates rendering to the WatchlistPage feature component.
 *
 * This follows the architecture pattern where route files only handle
 * parameter parsing (none needed here) and delegate business logic to feature components.
 */
const WatchlistPageRoute = memo(() => {
  // Log route initialization
  logger.debug("WatchlistPageRoute initializing");

  // Delegate to the feature component
  return <WatchlistPage />;
});

WatchlistPageRoute.displayName = "WatchlistPageRoute";

export default WatchlistPageRoute;
