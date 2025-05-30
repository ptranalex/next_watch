"use client";

import { memo, useState, useEffect, useMemo } from "react";
import { useParams } from "@/services/hooks";
import { MovieDetailPage } from "@/components/features/movies/detail";
import { createLogger } from "@/utils/logging";

// Create logger for this route
const logger = createLogger("MovieDetailRoute");

// Force dynamic to ensure latest movie data is fetched
export const dynamic = "force-dynamic";

interface MovieDetailPageRouteProps {
  params: Promise<{ id: string }> | { id: string };
}

/**
 * Movie Detail Page Route - /movies/[id]
 *
 * Route-level component that:
 * 1. Parses route parameters
 * 2. Delegates rendering to the MovieDetailPage feature component
 *
 * This follows the architecture pattern where route files only handle
 * parameter parsing and delegate business logic to feature components.
 */
const MovieDetailPageRoute = memo(
  ({ params: paramsPromise }: MovieDetailPageRouteProps) => {
    // Log route initialization
    logger.debug("MovieDetailPageRoute initializing");

    // Use our custom hook to handle params unwrapping
    const resolvedParams = useParams(paramsPromise);
    const [paramsResolved, setParamsResolved] = useState(false);

    // Track when params are resolved for initial loading state
    useEffect(() => {
      if (resolvedParams && Object.keys(resolvedParams).length > 0) {
        setParamsResolved(true);
        logger.debug("Route params resolved", { params: resolvedParams });
      }
    }, [resolvedParams]);

    // Parse movie ID from route parameters
    const movieId = useMemo(() => {
      return resolvedParams?.id ? Number(resolvedParams.id) : 0;
    }, [resolvedParams?.id]);

    // Log the extracted movie ID
    useEffect(() => {
      if (movieId) {
        logger.info(`Route resolved movie ID: ${movieId}`);
      }
    }, [movieId]);

    // Show loading state during initial params resolution
    if (!paramsResolved) {
      logger.debug("Waiting for params to resolve");
      return (
        <div className="text-center py-10">
          <p>Loading...</p>
        </div>
      );
    }

    // Delegate to the feature component
    return <MovieDetailPage movieId={movieId} />;
  }
);

MovieDetailPageRoute.displayName = "MovieDetailPageRoute";

export default MovieDetailPageRoute;
