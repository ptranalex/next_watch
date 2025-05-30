"use client";

import { memo, useState, useEffect } from "react";
import { useParams } from "@/services/hooks";
import { GenrePage } from "@/components/features/genres";
import { createLogger } from "@/utils/logging";

// Create logger for this route
const logger = createLogger("GenreRoute");

// Genre page route props interface
interface GenrePageRouteProps {
  params: Promise<{ id: string }> | { id: string };
}

/**
 * Genre Page Route - /genres/[id]
 *
 * Route-level component that:
 * 1. Parses route parameters
 * 2. Delegates rendering to the GenrePage feature component
 *
 * This follows the architecture pattern where route files only handle
 * parameter parsing and delegate business logic to feature components.
 */
const GenrePageRoute = memo(
  ({ params: paramsPromise }: GenrePageRouteProps) => {
    // Log route initialization
    logger.debug("GenrePageRoute initializing");

    // Safely unwrap params and extract genre ID
    const params = useParams(paramsPromise);
    const [paramsResolved, setParamsResolved] = useState(false);

    // Track when params are resolved for initial loading state
    useEffect(() => {
      if (params && Object.keys(params).length > 0) {
        setParamsResolved(true);
        logger.debug("Route params resolved", { params });
      }
    }, [params]);

    // Parse genre ID from route parameters
    const genreId = params?.id ? Number(params.id) : 0;

    // Log the extracted genre ID
    useEffect(() => {
      if (genreId) {
        logger.info(`Route resolved genre ID: ${genreId}`);
      }
    }, [genreId]);

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
    return <GenrePage genreId={genreId} />;
  }
);

GenrePageRoute.displayName = "GenrePageRoute";

export default GenrePageRoute;
