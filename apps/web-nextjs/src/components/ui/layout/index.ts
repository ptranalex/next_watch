/**
 * Templates Index
 *
 * Export point for all template components and their types.
 * Templates combine organisms, molecules, and atoms into complete page layouts.
 */

// ============================================================================
// Types
// ============================================================================

export type {
  BaseContainerProps,
  BaseGridProps,
  AppShellProps,
  ResponsiveShellProps,
  BrowseLayoutProps,
  DetailLayoutProps,
  DashboardLayoutProps,
  FormLayoutProps,
  SettingsLayoutProps,
  AuthLayoutProps,
  ErrorLayoutProps,
  NotFoundLayoutProps,
} from "./types";

// ============================================================================
// Components
// ============================================================================

// Layout templates
export { default as AppShell } from "./AppShell";
export { default as ResponsiveShell } from "./ResponsiveShell";

// Content templates
export { default as MovieBrowseLayout } from "./MovieBrowseLayout";
export { default as MovieBrowseLayoutSkeleton } from "./MovieBrowseLayoutSkeleton";
export { default as PageLayout } from "./PageLayout";
export { default as PageErrorBoundary } from "./PageErrorBoundary";

// Additional templates (to be implemented as needed)
// export { default as DetailLayout } from "./DetailLayout";
// export { default as DashboardLayout } from "./DashboardLayout";
// export { default as FormLayout } from "./FormLayout";
// export { default as SettingsLayout } from "./SettingsLayout";
// export { default as AuthLayout } from "./AuthLayout";
// export { default as ErrorLayout } from "./ErrorLayout";
// export { default as NotFoundLayout } from "./NotFoundLayout";
