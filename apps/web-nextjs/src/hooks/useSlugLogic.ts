"use client";

import { usePathname } from "next/navigation";

export function useSlugLogic() {
  const pathname = usePathname();

  // Simple logic to extract title from path
  // This is a placeholder implementation
  if (!pathname || pathname === "/") return "All Movies";

  // Extract from the URL path: /movies/category/action => "Action Movies"
  const segments = pathname.split("/").filter(Boolean);

  // If it's a movie category
  if (segments.length > 1 && segments[0] === "movies") {
    // Transform slugs: top-rated => Top Rated
    const category = segments[1]
      .split("-")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");

    return `${category} Movies`;
  }

  // Default fallback
  return "Movies";
}
