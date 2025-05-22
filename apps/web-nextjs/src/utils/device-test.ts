/**
 * Device Testing Utilities
 * Helps with testing mobile-first approach by providing device detection helpers
 */

import { useResponsive } from "@/providers/ResponsiveContext";
import { useEffect } from "react";
import { createLogger } from "@/utils/logging";

const logger = createLogger("DeviceTest");

/**
 * Hook to test device detection
 * Logs information about the current device for debugging
 */
export const useDeviceTest = () => {
  const { isMobile, isTablet, isDesktop, hasTouchScreen } = useResponsive();

  useEffect(() => {
    logger.info("Device detection test:", {
      isMobile,
      isTablet,
      isDesktop,
      hasTouchScreen,
      userAgent: typeof navigator !== "undefined" ? navigator.userAgent : "SSR",
      viewport: {
        width: typeof window !== "undefined" ? window.innerWidth : "SSR",
        height: typeof window !== "undefined" ? window.innerHeight : "SSR",
      },
    });
  }, [isMobile, isTablet, isDesktop, hasTouchScreen]);

  return {
    isMobile,
    isTablet,
    isDesktop,
    hasTouchScreen,
    deviceType: isMobile ? "mobile" : isTablet ? "tablet" : "desktop",
  };
};

/**
 * Simulates a mobile device for testing (client-side only)
 * Note: This is for development use only
 */
export const simulateMobileDevice = (enable = true) => {
  if (typeof window === "undefined") return; // Skip in SSR

  // Store original userAgent to restore it later
  if (!window.__originalUserAgent) {
    window.__originalUserAgent = navigator.userAgent;
  }

  // Modify the userAgent property if testing enabled
  if (enable) {
    // Override user agent with a mobile one
    Object.defineProperty(navigator, "userAgent", {
      get: function () {
        return "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1";
      },
      configurable: true,
    });

    logger.info("Mobile device simulation enabled");
  } else {
    // Restore original user agent
    Object.defineProperty(navigator, "userAgent", {
      get: function () {
        return window.__originalUserAgent;
      },
      configurable: true,
    });

    logger.info("Mobile device simulation disabled");
  }
};

// Add type definition for window object extension
declare global {
  interface Window {
    __originalUserAgent?: string;
  }
}
