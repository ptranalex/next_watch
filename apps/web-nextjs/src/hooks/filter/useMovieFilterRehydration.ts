"use client";

import { usePathname, useSearchParams } from "next/navigation";
import { useEffect } from "react";
import useMovieFilterStore from "@/store/movieFilterStore";

export function useMovieFilterRehydration() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { setFilter, unlockFilters } = useMovieFilterStore();

  useEffect(() => {
    if (!pathname || !searchParams) return;

    // SAFETY: Always unlock all filters first
    unlockFilters();

    // Set filters from query params
    const entries = Array.from(searchParams.entries()) as [string, string][];
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
          setFilter(key as any, numericValue);
        }
      } else if (key === "sortOrder") {
        setFilter("sortOrder", value);
      }
    }
  }, []); // ✅ Run only once on mount
}
