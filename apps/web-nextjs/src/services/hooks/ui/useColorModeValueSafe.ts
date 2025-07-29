import { useColorModeValue } from "@chakra-ui/react";
import { useState, useEffect } from "react";

/**
 * Hydration-safe version of useColorModeValue
 *
 * Prevents the light->dark flash during hydration by:
 * 1. Detecting system preference during SSR when possible
 * 2. Using smart defaults that match the likely system preference
 * 3. Only switching to actual color mode values after hydration
 *
 * This handles the timing issue where Chakra UI's system detection
 * happens after hydration, causing a flash.
 */
export function useColorModeValueSafe<TLight = unknown, TDark = unknown>(
  light: TLight,
  dark: TDark
): TLight | TDark {
  // Track hydration state
  const [isHydrated, setIsHydrated] = useState(false);
  const [systemPreference, setSystemPreference] = useState<string | null>(null);

  // Get the actual color mode values
  const colorModeValue = useColorModeValue(light, dark);

  // Detect system preference as early as possible
  useEffect(() => {
    if (typeof window !== "undefined") {
      const darkModeQuery = window.matchMedia("(prefers-color-scheme: dark)");
      const lightModeQuery = window.matchMedia("(prefers-color-scheme: light)");

      if (darkModeQuery.matches) {
        setSystemPreference("dark");
      } else if (lightModeQuery.matches) {
        setSystemPreference("light");
      } else {
        setSystemPreference("no-preference");
      }
    }

    setIsHydrated(true);
  }, []);

  // If we're not hydrated yet, use the detected system preference
  if (!isHydrated) {
    // If we detected system preference, use it
    if (systemPreference === "dark") {
      return dark;
    } else if (systemPreference === "light") {
      return light;
    }

    // If no system preference detected, default to dark mode
    // (statistically more likely for developers and movie app users)
    return dark;
  }

  // After hydration, use the actual Chakra color mode value
  return colorModeValue;
}

export default useColorModeValueSafe;
