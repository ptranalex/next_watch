"use client";

import { memo } from "react";
import { LikedPage } from "@/components/features/movies/liked";
import { createLogger } from "@/utils/logging";

// Create logger for this route
const logger = createLogger("LikedPageRoute");

/**
 * Liked Page Route - /liked
 *
 * Route-level component that delegates rendering to the LikedPage feature component.
 *
 * This follows the architecture pattern where route files only handle
 * parameter parsing (none needed here) and delegate business logic to feature components.
 */
const LikedPageRoute = memo(() => {
  // Log route initialization
  logger.debug("LikedPageRoute initializing");

  // Delegate to the feature component
  return <LikedPage />;
});

LikedPageRoute.displayName = "LikedPageRoute";

export default LikedPageRoute;
