"use client";

import { useEffect } from "react";
import { createLogger } from "@/utils/logging";

const logger = createLogger("AppHeightScript");

/**
 * AppHeightScript component
 * Sets the correct height variable for mobile browsers to handle 100vh correctly
 * This is necessary for proper scroll position calculation on mobile devices
 */
export default function AppHeightScript() {
  useEffect(() => {
    const setAppHeight = () => {
      const height = `${window.innerHeight}px`;
      document.documentElement.style.setProperty("--app-height", height);
      logger.debug(`Setting app height to ${height}`);
    };

    // Set initial height
    setAppHeight();

    // Log initial window dimensions
    logger.info("Initializing viewport dimensions:", {
      innerHeight: window.innerHeight,
      innerWidth: window.innerWidth,
      scrollY: window.scrollY,
      documentHeight: document.documentElement.scrollHeight,
    });

    // Update on resize and orientation change
    window.addEventListener("resize", setAppHeight);
    window.addEventListener("orientationchange", setAppHeight);

    // Clean up event listeners
    return () => {
      window.removeEventListener("resize", setAppHeight);
      window.removeEventListener("orientationchange", setAppHeight);
    };
  }, []);

  return null; // This component doesn't render anything
}
