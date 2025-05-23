import { BaseModalProps } from "@/components/ui/types";

/**
 * Profile Feature Types
 *
 * Types specific to profile components including modals,
 * statistics, and preferences.
 */

// ============================================================================
// Profile Component Props
// ============================================================================

/** Profile modal props */
export interface ProfileModalProps extends BaseModalProps {
  activeTab?: "profile" | "preferences" | "history";
}

/** Import history modal props */
export interface ImportHistoryModalProps extends BaseModalProps {
  supportedFormats?: string[];
  maxFileSize?: number;
  onImportComplete?: (importedCount: number) => void;
}

/** Profile stats props */
export interface ProfileStatsProps {
  totalMovies?: number;
  watchedMovies?: number;
  likedMovies?: number;
  watchlistMovies?: number;
  showPercentages?: boolean;
}

/** Profile preferences props */
export interface ProfilePreferencesProps {
  onPreferenceChange?: (key: string, value: unknown) => void;
  preferences?: Record<string, unknown>;
}
