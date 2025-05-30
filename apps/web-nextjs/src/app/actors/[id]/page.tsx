"use client";

import { memo, useState, useEffect } from "react";
import { useParams } from "@/services/hooks";
import { ActorPage } from "@/components/features/actors";
import { createLogger } from "@/utils/logging";

// Create logger for this route
const logger = createLogger("ActorRoute");

// Actor page route props interface
interface ActorPageRouteProps {
  params: Promise<{ id: string }> | { id: string };
}

/**
 * Actor Page Route - /actors/[id]
 *
 * Route-level component that:
 * 1. Parses route parameters
 * 2. Delegates rendering to the ActorPage feature component
 *
 * This follows the architecture pattern where route files only handle
 * parameter parsing and delegate business logic to feature components.
 */
const ActorPageRoute = memo(
  ({ params: paramsPromise }: ActorPageRouteProps) => {
    // Log route initialization
    logger.debug("ActorPageRoute initializing");

    // Safely unwrap params and extract actor ID
    const params = useParams(paramsPromise);
    const [paramsResolved, setParamsResolved] = useState(false);

    // Track when params are resolved for initial loading state
    useEffect(() => {
      if (params && Object.keys(params).length > 0) {
        setParamsResolved(true);
        logger.debug("Route params resolved", { params });
      }
    }, [params]);

    // Parse actor ID from route parameters
    const actorId = params?.id ? Number(params.id) : 0;

    // Log the extracted actor ID
    useEffect(() => {
      if (actorId) {
        logger.info(`Route resolved actor ID: ${actorId}`);
      }
    }, [actorId]);

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
    return <ActorPage actorId={actorId} />;
  }
);

ActorPageRoute.displayName = "ActorPageRoute";

export default ActorPageRoute;
