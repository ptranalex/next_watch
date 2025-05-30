"use client";

import { memo } from "react";
import { ProfilePage } from "@/components/features/profile";
import { createLogger } from "@/utils/logging";

// Create logger for this route
const logger = createLogger("ProfilePageRoute");

// Make the page dynamic to avoid prerendering issues
export const dynamic = "force-dynamic";

/**
 * Profile Page Route - /profile
 *
 * Route-level component that delegates rendering to the ProfilePage feature component.
 *
 * This follows the architecture pattern where route files only handle
 * parameter parsing (none needed here) and delegate business logic to feature components.
 */
const ProfilePageRoute = memo(() => {
  // Log route initialization
  logger.debug("ProfilePageRoute initializing");

  // Delegate to the feature component
  return <ProfilePage />;
});

ProfilePageRoute.displayName = "ProfilePageRoute";

export default ProfilePageRoute;
