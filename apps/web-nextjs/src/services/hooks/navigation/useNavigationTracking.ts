"use client";

import { usePathname, useSearchParams } from "next/navigation";
import { useEffect, useRef } from "react";
import { useAnalytics } from "@/services/hooks/core";
import { createLogger } from "@/utils/logging";

const logger = createLogger("navigationTracking");

/**
 * Hook to automatically track navigation between pages
 *
 * This hook monitors route changes and automatically sends
 * navigation events to Google Analytics.
 *
 * Usage: Simply call this hook in your root layout or app component.
 * Note: Must be wrapped in Suspense boundary for SSR compatibility.
 */
export function useNavigationTracking() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const analytics = useAnalytics();
  const previousPathRef = useRef<string | null>(null);
  const isInitialLoadRef = useRef(true);

  // Debug: Log hook initialization
  useEffect(() => {
    logger.info("🚀 Navigation tracking hook initialized", {
      pathname,
      searchParams: searchParams?.toString(),
    });
  }, [pathname, searchParams]);

  useEffect(() => {
    // Construct full URL with search params
    const currentPath =
      pathname +
      (searchParams?.toString() ? `?${searchParams.toString()}` : "");
    const previousPath = previousPathRef.current;

    logger.debug("🔍 Navigation effect triggered", {
      currentPath,
      previousPath,
      isInitialLoad: isInitialLoadRef.current,
    });

    // Skip tracking on initial page load (GA handles this automatically)
    if (isInitialLoadRef.current) {
      isInitialLoadRef.current = false;
      previousPathRef.current = currentPath;
      logger.info(
        "📍 Initial page load detected, skipping navigation tracking",
        {
          currentPath,
        }
      );
      return;
    }

    // Track navigation if the path actually changed
    if (previousPath && previousPath !== currentPath) {
      logger.info("🧭 Navigation detected", {
        from: previousPath,
        to: currentPath,
      });

      // Track the navigation event
      const navigationSuccess = analytics.trackNavigation(
        currentPath,
        previousPath
      );
      logger.debug("Navigation event result:", navigationSuccess);

      // Also track as a custom page view for SPA navigation
      const pageViewSuccess = analytics.trackPage(
        currentPath,
        getPageTitle(pathname)
      );
      logger.debug("Page view event result:", pageViewSuccess);
    } else {
      logger.debug("🔄 No navigation change detected", {
        currentPath,
        previousPath,
        changed: previousPath !== currentPath,
      });
    }

    // Update previous path reference
    previousPathRef.current = currentPath;
  }, [pathname, searchParams, analytics]);
}

/**
 * Helper function to generate meaningful page titles from pathnames
 */
function getPageTitle(pathname: string): string {
  // Define route to title mapping
  const routeTitles: Record<string, string> = {
    "/": "Home",
    "/movies": "Movies",
    "/search": "Search",
    "/watchlist": "Watchlist",
    "/watched": "Watched Movies",
    "/liked": "Liked Movies",
    "/profile": "Profile",
    "/settings": "Settings",
  };

  // Check for exact matches
  if (routeTitles[pathname]) {
    return routeTitles[pathname];
  }

  // Handle dynamic routes
  if (pathname.startsWith("/movies/")) {
    const movieId = pathname.split("/")[2];
    return `Movie ${movieId}`;
  }

  if (pathname.startsWith("/actors/")) {
    const actorId = pathname.split("/")[2];
    return `Actor ${actorId}`;
  }

  if (pathname.startsWith("/genres/")) {
    const genreId = pathname.split("/")[2];
    return `Genre ${genreId}`;
  }

  // Fallback: capitalize and format pathname
  return (
    pathname
      .split("/")
      .filter(Boolean)
      .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
      .join(" ") || "Page"
  );
}
