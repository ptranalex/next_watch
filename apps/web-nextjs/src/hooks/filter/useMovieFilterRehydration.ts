"use client";

import { usePathname, useSearchParams } from "next/navigation";
import { useEffect } from "react";
import useMovieFilterStore from "@/store/movieFilterStore";
import { createLogger } from "@/utils/logging";

// Create logger for this hook
const logger = createLogger("useMovieFilterRehydration");

export function useMovieFilterRehydration() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { setFilter, unlockFilters } = useMovieFilterStore();

  // Log hook initialization
  logger.debug("useMovieFilterRehydration initialized");

  useEffect(() => {
    if (!pathname || !searchParams) {
      logger.debug("Missing pathname or searchParams, skipping rehydration");
      return;
    }

    // SAFETY: Always unlock all filters first
    logger.debug("Unlocking all filters");
    unlockFilters();

    // Set filters from query params
    const entries = Array.from(searchParams.entries()) as [string, string][];

    if (entries.length === 0) {
      logger.debug("No search params to rehydrate");
      return;
    }

    logger.info(`Rehydrating ${entries.length} filters from URL params`);

    for (const [key, value] of entries) {
      if (
        [
          "imdb_rating",
          "rotten_tomatoes_rating",
          "metacritic_rating",
          "year",
        ].includes(key)
      ) {
        const numericValue = Number(value);
        if (!isNaN(numericValue)) {
          logger.debug(`Setting numeric filter: ${key}=${numericValue}`);
          setFilter(key as any, numericValue);
        }
      } else if (key === "sortOrder") {
        logger.debug(`Setting sort order: ${value}`);
        setFilter("sortOrder", value);
      }
    }
  }, []); // ✅ Run only once on mount
}
