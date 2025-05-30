"use client";

import { memo } from "react";
import { HomePage } from "@/components/features/movies/home";
import { createLogger } from "@/utils/logging";

// Create logger for this route
const logger = createLogger("HomePageRoute");

// Make the page dynamic to avoid prerendering issues
export const dynamic = "force-dynamic";

/**
 * Home Page Route - /
 *
 * Route-level component that delegates rendering to the HomePage feature component.
 *
 * This follows the architecture pattern where route files only handle
 * parameter parsing (none needed here) and delegate business logic to feature components.
 */
const HomePageRoute = memo(() => {
  // Log route initialization
  logger.debug("HomePageRoute initializing");

  // Delegate to the feature component
  return <HomePage />;
});

HomePageRoute.displayName = "HomePageRoute";

export default HomePageRoute;
