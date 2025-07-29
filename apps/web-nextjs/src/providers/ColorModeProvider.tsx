"use client";

import { ReactNode, useEffect, useState } from "react";
import LoadingSpinner from "@/components/ui/atoms/LoadingSpinner";

interface ColorModeProviderProps {
  children: ReactNode;
}

/**
 * ColorModeProvider that prevents color mode flashing by waiting for proper hydration
 *
 * This component ensures that:
 * 1. We don't render content until the color mode is properly detected
 * 2. System preference is correctly applied before first paint
 * 3. No light->dark flashing occurs during hydration
 *
 * Uses the reusable LoadingSpinner component for consistent UX
 */
export function ColorModeProvider({ children }: ColorModeProviderProps) {
  const [isColorModeReady, setIsColorModeReady] = useState(false);
  const [systemPreference, setSystemPreference] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      // Detect actual system preference
      const darkModeQuery = window.matchMedia("(prefers-color-scheme: dark)");
      const lightModeQuery = window.matchMedia("(prefers-color-scheme: light)");

      let detectedPreference = "dark"; // default fallback
      if (darkModeQuery.matches) {
        detectedPreference = "dark";
      } else if (lightModeQuery.matches) {
        detectedPreference = "light";
      }

      setSystemPreference(detectedPreference);

      // Small delay to ensure Chakra UI has time to apply the correct color mode
      const timer = setTimeout(() => {
        setIsColorModeReady(true);
      }, 50); // Minimal delay to prevent flash

      return () => clearTimeout(timer);
    }
  }, []);

  // Don't render children until color mode is properly set
  if (!isColorModeReady) {
    const isDark = systemPreference !== "light";

    return (
      <div
        style={{
          backgroundColor: isDark ? "***REMOVED***0d1117" : "***REMOVED***ffffff",
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <LoadingSpinner
          size={36}
          speed={1.5} // Faster animation for responsive feel
          showBranding={true}
          theme={isDark ? "dark" : "light"}
        />
      </div>
    );
  }

  return <>{children}</>;
}

export default ColorModeProvider;
