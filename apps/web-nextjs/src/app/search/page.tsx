"use client";

import { memo } from "react";
import { SearchPage } from "@/components/features/search";
import { createLogger } from "@/utils/logging";

// Create logger for this route
const logger = createLogger("SearchPageRoute");

/**
 * Search Page Route - /search
 *
 * Route-level component that delegates rendering to the SearchPage feature component.
 *
 * This follows the architecture pattern where route files only handle
 * parameter parsing (search params handled by feature component) and delegate business logic to feature components.
 *
 * Features:
 * - Real-time search with debouncing
 * - Advanced filtering (genre, year, rating, etc.)
 * - Responsive design with mobile optimization
 * - SEO optimized with proper metadata
 */
const SearchPageRoute = memo(() => {
  // Log route initialization
  logger.debug("SearchPageRoute initializing");

  // Delegate to the feature component
  return <SearchPage />;
});

SearchPageRoute.displayName = "SearchPageRoute";

export default SearchPageRoute;
