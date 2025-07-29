"use client";

import { memo, useState, useEffect, useMemo } from "react";
import { TopMoviesPage } from "@/components/features/movies/top";
import TopMoviesPageSkeleton from "@/components/features/movies/top/TopMoviesPageSkeleton";
import { createLogger } from "@/utils/logging";

// Create logger for this route
const logger = createLogger("TopMoviesPageRoute");

// Make the page dynamic to avoid prerendering issues
export const dynamic = "force-dynamic";

interface TopMoviesPageRouteProps {
  params: Promise<{ year: string }> | { year: string };
}

/**
 * Top Movies Page Route - /top/[year]
 *
 * Route-level component that:
 * 1. Parses route parameters (year)
 * 2. Delegates rendering to the TopMoviesPage feature component
 *
 * This follows the architecture pattern where route files only handle
 * parameter parsing and delegate business logic to feature components.
 *
 * Special cases handled:
 * - top/current-year: Uses the current year and locks it
 * - top/all-time: Shows all years, no year filter is locked
 */
const TopMoviesPageRoute = memo(
  ({ params: paramsPromise }: TopMoviesPageRouteProps) => {
    // Log route initialization
    logger.debug("TopMoviesPageRoute initializing");

    // Handle both Promise and direct params (Next.js 15 compatibility)
    const [resolvedParams, setResolvedParams] = useState<{
      year: string;
    } | null>(null);
    const [paramsResolved, setParamsResolved] = useState(false);

    // Resolve params if they're a Promise
    useEffect(() => {
      const resolveParams = async () => {
        try {
          const params = await Promise.resolve(paramsPromise);
          setResolvedParams(params);
          setParamsResolved(true);
          logger.debug("Route params resolved", { params });
        } catch (error) {
          logger.error("Error resolving params:", error);
          setParamsResolved(true);
        }
      };

      resolveParams();
    }, [paramsPromise]);

    // Parse year parameter from route
    const yearParam = useMemo(() => {
      return resolvedParams?.year || "";
    }, [resolvedParams?.year]);

    // Log the extracted year parameter
    useEffect(() => {
      if (yearParam) {
        logger.info(`Route resolved year parameter: ${yearParam}`);
      }
    }, [yearParam]);

    // Show skeleton loading state during initial params resolution
    // Industry standard: skeleton that matches actual content structure
    if (!paramsResolved) {
      logger.debug("Waiting for params to resolve - showing skeleton");
      return <TopMoviesPageSkeleton />;
    }

    // Delegate to the feature component
    return <TopMoviesPage yearParam={yearParam} />;
  }
);

TopMoviesPageRoute.displayName = "TopMoviesPageRoute";

export default TopMoviesPageRoute;
