/**
 * Loading UI for Movie Detail Page Route - /movies/[id]/loading.tsx
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

import MovieDetailPageSkeleton from "@/components/features/movies/detail/MovieDetailPageSkeleton";

export default function Loading() {
  return <MovieDetailPageSkeleton />;
}
