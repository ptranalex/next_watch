"use client";

import React, { useEffect } from "react";
import AppShell from "@/components/ui/templates/AppShell";
import { MobileAppShell } from "@/components/mobile/core/layout";
import { useResponsive } from "@/providers/ResponsiveContext";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("ResponsiveShell");

/**
 * ResponsiveShell component
 * Intelligently selects the appropriate shell based on device capabilities
 * True mobile-first approach: use dedicated mobile components rather than just responsive design
 * SSR-safe: always renders desktop shell during SSR for minimal layout shifts
 */
export default function ResponsiveShell({
  children,
}: {
  children: React.ReactNode;
}) {
  // Use the centralized responsive context instead of direct media queries
  const { isMobile, isTablet, isDesktop, hasTouchScreen, isHydrated } =
    useResponsive();

  // Log which shell is being used along with detailed device information
  useEffect(() => {
    if (isHydrated) {
      logger.info(
        `ResponsiveShell mounted - using ${
          isDesktop ? "desktop" : isMobile ? "mobile" : "tablet"
        } shell`
      );

      logger.debug(
        `Device details: mobile=${isMobile}, tablet=${isTablet}, desktop=${isDesktop}, touch=${hasTouchScreen}`
      );
    }
  }, [isMobile, isTablet, isDesktop, hasTouchScreen, isHydrated]);

  // SSR-safe default shell: always render AppShell during SSR
  // Only switch to MobileAppShell after hydration if on mobile
  // This provides a complete-looking experience immediately with minimal layout shift
  if (!isHydrated || !isMobile) {
    return <AppShell>{children}</AppShell>;
  }

  // Only render mobile shell after hydration is complete and we've confirmed mobile device
  return <MobileAppShell>{children}</MobileAppShell>;
}
