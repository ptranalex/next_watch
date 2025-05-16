"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import useMovieFilterStore from "@/store/movieFilterStore";

export function useSyncFiltersToUrl() {
  const { filters } = useMovieFilterStore();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        params.set(key, String(value));
      }
    });

    const queryString = params.toString();
    const newUrl = `${pathname}${queryString ? `?${queryString}` : ""}`;

    router.replace(newUrl, { scroll: false });
  }, [filters, pathname]);
}
