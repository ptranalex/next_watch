/**
 * Cross-Cutting Feature Types
 *
 * Types that are shared across multiple feature domains or provide
 * foundational patterns for feature development.
 */

// ============================================================================
// Cross-Cutting Utility Types
// ============================================================================

/** Feature flag props */
export interface FeatureFlagProps {
  children: React.ReactNode;
  feature: string;
  fallback?: React.ReactNode;
}

/** Analytics event props */
export interface AnalyticsEventProps {
  event: string;
  properties?: Record<string, unknown>;
  userId?: string;
}

/** Error boundary for features */
export interface FeatureErrorBoundaryProps {
  children: React.ReactNode;
  feature: string;
  fallback?: React.ComponentType<{ error: Error; retry: () => void }>;
  onError?: (error: Error, feature: string) => void;
}

/** Feature loading states */
export type FeatureLoadingState =
  | "idle"
  | "loading"
  | "loaded"
  | "error"
  | "refreshing";

/** Feature async operation */
export interface FeatureAsyncOperation<T = unknown> {
  data?: T;
  loading: boolean;
  error?: string;
  retry: () => void;
  refresh: () => void;
}
