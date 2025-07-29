/**
 * Loading UI for Top Movies Page Route - /top/[year]/loading.tsx
 *
 * Next.js App Router automatically shows this component during navigation
 * and while the page component is loading. This is the industry standard
 * approach for handling loading states in Next.js 13+.
 *
 * Benefits:
 * - Automatic loading UI without manual state management
 * - Instant rendering (no delay waiting for params)
 * - Consistent loading experience across the app
 * - Better Core Web Vitals (Cumulative Layout Shift)
 */

import TopMoviesPageSkeleton from "@/components/features/movies/top/TopMoviesPageSkeleton";

export default function Loading() {
  return <TopMoviesPageSkeleton />;
}
