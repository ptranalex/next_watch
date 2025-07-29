"use client";

import LoadingSpinner from "@/components/ui/atoms/LoadingSpinner";
import LoadingIndicator from "@/components/ui/molecules/LoadingIndicator";
import { createLogger } from "@/utils/logging";
import { useEffect, useState } from "react";

// Create logger for this component
const logger = createLogger("LoadingPage");

/**
 * Smart loading UI for Next.js App Router
 *
 * Strategy:
 * - First 300ms: Show top progress bar (non-blocking, for quick navigation)
 * - After 300ms: Show center spinner (for slower loads that need clear feedback)
 *
 * This gives the best UX for both quick and slow page transitions.
 */
export default function Loading() {
  const [showCenterSpinner, setShowCenterSpinner] = useState(false);

  // Log loading state
  useEffect(() => {
    logger.debug("Route loading state activated");

    // Switch to center spinner after 300ms if still loading
    const timer = setTimeout(() => {
      setShowCenterSpinner(true);
      logger.debug("Switching to center spinner for longer load");
    }, 300);

    return () => {
      clearTimeout(timer);
      logger.debug("Route loading state completed");
    };
  }, []);

  return (
    <>
      {/* Always show top progress bar immediately */}
      <LoadingIndicator />

      {/* Show center spinner for longer loads */}
      {showCenterSpinner && (
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            minHeight: "40vh",
            flexDirection: "column",
          }}
        >
          <LoadingSpinner size={36} speed={1.2} showBranding />
        </div>
      )}
    </>
  );
}
