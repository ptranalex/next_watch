"use client";

import { useEffect, useRef } from "react";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import useMovieFilterStore from "@/store/movieFilterStore";

export function useSyncFiltersToUrl() {
  const { filters, isFilterLocked } = useMovieFilterStore();
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const lastUpdateRef = useRef<number>(0);
  const lastUrlRef = useRef<string>("");

  useEffect(() => {
    // Throttle updates to prevent rapid consecutive URL changes
    const now = Date.now();
    if (now - lastUpdateRef.current < 300) {
      return; // Don't update if less than 300ms have passed
    }

    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      // Skip locked filters - they're encoded in the path
      if (isFilterLocked(key as any)) {
        return;
      }

      // Skip empty values
      if (value !== undefined && value !== null && value !== "") {
        params.set(key, String(value));
      }
    });

    const queryString = params.toString();
    const newUrl = `${pathname}${queryString ? `?${queryString}` : ""}`;

    // Don't update if URL isn't changing to avoid unnecessary navigation
    if (newUrl === lastUrlRef.current) {
      return;
    }

    // Check if the new URL params match the current URL params
    let currentParamsEqual = true;
    const currentParams = searchParams;

    // Compare current params with what we're about to set
    if (currentParams) {
      if (currentParams.toString() !== params.toString()) {
        currentParamsEqual = false;
      }
    } else if (params.toString()) {
      // Current has no params but we're about to add some
      currentParamsEqual = false;
    }

    // Only navigate if params have actually changed
    if (!currentParamsEqual) {
      lastUpdateRef.current = now;
      lastUrlRef.current = newUrl;
      router.replace(newUrl, { scroll: false });
    }
  }, [filters, pathname, router, isFilterLocked, searchParams]);
}
