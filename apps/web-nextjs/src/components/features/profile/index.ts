/**
 * Profile Feature Components
 *
 * This module exports all profile-related components and types.
 */

// ============================================================================
// Types
// ============================================================================

export type {
  ProfileModalProps,
  ImportHistoryModalProps,
  ProfileStatsProps,
  ProfilePreferencesProps,
} from "./types";

// ============================================================================
// Components
// ============================================================================

export { default as ProfileModal } from "./ProfileModal";
export { default as ImportNetflixHistoryModal } from "./ImportNetflixHistoryModal";

// TODO: Export these components when they are created
// export { default as ProfileStats } from "./ProfileStats";
// export { default as ProfilePreferences } from "./ProfilePreferences";
