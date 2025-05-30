"use client";

import { Suspense, useEffect } from "react";
import { useNavigationTracking } from "@/services/hooks";

/**
 * Internal component that uses useSearchParams
 * This needs to be wrapped in Suspense for SSR compatibility
 */
function NavigationTrackingImpl() {
  useNavigationTracking();
  return null;
}

/**
 * Navigation Tracker Component
 *
 * A client-side component that automatically tracks navigation
 * events throughout the application. Should be placed in the
 * root layout to monitor all route changes.
 */
export default function NavigationTracker() {
  useEffect(() => {
    console.log("🔧 NavigationTracker component mounted");
  }, []);

  return (
    <Suspense fallback={null}>
      <NavigationTrackingImpl />
    </Suspense>
  );
}
