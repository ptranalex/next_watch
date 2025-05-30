"use client";

import React, { useEffect } from "react";
import AppShell from "@/components/ui/layout/AppShell";
import { MobileAppShell } from "@/components/mobile/core/layout";
import { useResponsive } from "@/providers/ResponsiveContext";
import { createLogger } from "@/utils/logging";
import type { ResponsiveShellProps } from "./types";

// Create logger for this component
const logger = createLogger("ResponsiveShell");

/**
 * ResponsiveShell component using shared ResponsiveShellProps
 *
 * Intelligently selects the appropriate shell based on device capabilities.
 * True mobile-first approach: use dedicated mobile components rather than just responsive design.
 * SSR-safe: always renders desktop shell during SSR for minimal layout shifts.
 *
 * @param children - Main content area
 * @param header - Header content (passed to shell components)
 * @param sidebar - Sidebar content (passed to shell components)
 * @param footer - Footer content (passed to shell components)
 * @param breakpoint - Responsive breakpoint for shell switching (default: "lg")
 */
export default function ResponsiveShell({
  children,
  header,
  sidebar,
  footer,
  breakpoint = "lg",
}: ResponsiveShellProps) {
  // Use the centralized responsive context instead of direct media queries
  const { isMobile, isTablet, isDesktop, hasTouchScreen, isHydrated } =
    useResponsive();

  // Log which shell is being used along with detailed device information
  useEffect(() => {
    if (isHydrated) {
      logger.info(
        `ResponsiveShell mounted - using ${
          isDesktop ? "desktop" : isMobile ? "mobile" : "tablet"
        } shell (breakpoint: ${breakpoint})`
      );

      logger.debug(
        `Device details: mobile=${isMobile}, tablet=${isTablet}, desktop=${isDesktop}, touch=${hasTouchScreen}`
      );
    }
  }, [isMobile, isTablet, isDesktop, hasTouchScreen, isHydrated, breakpoint]);

  // Determine which shell to use based on breakpoint
  const shouldUseMobileShell = () => {
    switch (breakpoint) {
      case "sm":
        return isMobile;
      case "md":
        return isMobile || isTablet;
      case "lg":
      default:
        return isMobile;
      case "xl":
        return isMobile || isTablet;
    }
  };

  // SSR-safe default shell: always render AppShell during SSR
  // Only switch to MobileAppShell after hydration if conditions are met
  if (!isHydrated || !shouldUseMobileShell()) {
    return (
      <AppShell header={header} sidebar={sidebar} footer={footer}>
        {children}
      </AppShell>
    );
  }

  // Only render mobile shell after hydration is complete and conditions are met
  // Note: MobileAppShell doesn't support all props yet, so pass children only
  return <MobileAppShell>{children}</MobileAppShell>;
}
