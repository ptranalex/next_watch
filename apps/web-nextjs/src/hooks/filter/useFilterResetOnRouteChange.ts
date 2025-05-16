import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";
import { shouldResetFilters } from "@/hooks/filter/shouldResetFilters";
import useMovieFilterStore from "@/store/movieFilterStore";

export function useFilterResetOnRouteChange() {
  const pathname = usePathname();
  const prevPath = useRef<string | null>(null);
  const { resetFilters } = useMovieFilterStore();

  useEffect(() => {
    const from = prevPath.current;
    const to = pathname;

    // Always log first mount for debugging
    if (from === null) {
      console.log("🔹 First mount:", to);
      prevPath.current = to;
      return;
    }

    // Only log and handle actual transitions
    if (from !== to) {
      console.log("from", from, "to", to);

      const shouldReset = shouldResetFilters(from, to);
      console.log("shouldReset", shouldReset);

      if (shouldReset) {
        console.log("resetting filters on route change");
        resetFilters();
      }
    }

    prevPath.current = to;
  }, [pathname]);
}
