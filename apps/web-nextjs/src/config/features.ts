export const FEATURES = {
  SHOW_MORE_LIKE_THIS: false,
} as const;

// Type for feature flags
export type FeatureFlag = keyof typeof FEATURES;
