"use client";

import LoadingIndicator from "@/components/ui/molecules/LoadingIndicator";
import { createLogger } from "@/utils/logging";
import { useEffect } from "react";

// Create logger for this component
const logger = createLogger("LoadingPage");

export default function Loading() {
  // Log loading state
  useEffect(() => {
    logger.debug("Application loading state activated");
    return () => {
      logger.debug("Application loading state completed");
    };
  }, []);

  return <LoadingIndicator />;
}
