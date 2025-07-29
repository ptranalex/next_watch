/**
 * Loading UI for Actor Page Route - /actors/[id]/loading.tsx
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

import ActorPageSkeleton from "@/components/features/actors/ActorPageSkeleton";

export default function Loading() {
  return <ActorPageSkeleton />;
}
