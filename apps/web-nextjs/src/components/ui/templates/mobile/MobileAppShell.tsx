"use client";

import React, { memo, Suspense, useEffect } from "react";
import { Box, Spinner } from "@chakra-ui/react";
import { createLogger } from "@/utils/logging";
import MobileHeader from "@/components/ui/organisms/navigation/mobile/MobileHeader";

// Create logger for this component
const logger = createLogger("MobileAppShell");

/**
 * Content with suspense wrapper
 */
const ContentWithSuspense = ({ children }: { children: React.ReactNode }) => {
  return (
    <Suspense
      fallback={
        <Box display="flex" justifyContent="center" py={10}>
          <Spinner size="xl" />
        </Box>
      }
    >
      {children}
    </Suspense>
  );
};

/**
 * MobileAppShell component
 * Dedicated mobile layout with top header navigation only
 * No bottom navigation bar to maximize content space
 */
function MobileAppShell({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    logger.info("MobileAppShell mounted - rendering mobile-first layout");

    return () => {
      logger.debug("MobileAppShell unmounting");
    };
  }, []);

  return (
    <Box
      as="main"
      className="mobile-app-shell"
      // Full width on mobile
      width="100%"
      // Add safe area insets for mobile devices
      sx={{
        // Add iOS safe area support
        paddingBottom: "env(safe-area-inset-bottom, 0px)",
        paddingLeft: "env(safe-area-inset-left, 0px)",
        paddingRight: "env(safe-area-inset-right, 0px)",
      }}
    >
      {/* Top mobile header */}
      <MobileHeader />

      <Box
        className="mobile-content"
        // Mobile-optimized padding
        px={4}
        // Add bottom spacing for safe area
        pb={4}
        // Add top spacing
        pt={1}
      >
        <ContentWithSuspense>{children}</ContentWithSuspense>
      </Box>
    </Box>
  );
}

// Export the memoized component to prevent unnecessary re-renders
export default memo(MobileAppShell);
