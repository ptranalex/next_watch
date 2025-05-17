import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";
import { shouldResetFilters } from "@/hooks/filter/shouldResetFilters";
import useMovieFilterStore from "@/store/movieFilterStore";
import { createLogger } from "@/utils/logging";

// Create logger for this hook
const logger = createLogger("useFilterResetOnRouteChange");

export function useFilterResetOnRouteChange() {
  const pathname = usePathname();
  const prevPath = useRef<string | null>(null);
  const { resetFilters } = useMovieFilterStore();

  // Log hook initialization
  logger.debug("useFilterResetOnRouteChange initialized");

  useEffect(() => {
    const from = prevPath.current;
    const to = pathname;

    // Always log first mount for debugging
    if (from === null) {
      logger.debug(`First mount: ${to}`);
      prevPath.current = to;
      return;
    }

    // Only log and handle actual transitions
    if (from !== to) {
      logger.debug(`Route changed from: ${from} to: ${to}`);

      const shouldReset = shouldResetFilters(from, to);
      logger.debug(`Should reset filters: ${shouldReset}`);

      if (shouldReset) {
        logger.info("Resetting filters due to route change");
        resetFilters();
      }
    }

    prevPath.current = to;
  }, [pathname, resetFilters]);
}
