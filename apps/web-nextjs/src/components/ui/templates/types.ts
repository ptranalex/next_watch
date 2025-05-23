import type { ResponsiveBreakpoints } from "../atoms/types";

/**
 * Template Component Types
 *
 * Types for page-level templates that define complete layouts and structures,
 * combining organisms, molecules, and atoms into full page experiences.
 */

// ============================================================================
// Layout Templates
// ============================================================================

/** Base container props with responsive behavior */
export interface BaseContainerProps {
  maxWidth?: string | ResponsiveBreakpoints;
  centerContent?: boolean;
  padding?: string | ResponsiveBreakpoints;
  children: React.ReactNode;
}

/** Grid layout props pattern */
export interface BaseGridProps {
  columns?: ResponsiveBreakpoints;
  gap?: string | number;
  autoFlow?: "row" | "column" | "dense" | "row dense" | "column dense";
  children: React.ReactNode;
}

/** Shell template props for app-wide layout */
export interface AppShellProps {
  header?: React.ReactNode;
  sidebar?: React.ReactNode;
  footer?: React.ReactNode;
  children: React.ReactNode;
  isSidebarOpen?: boolean;
  onSidebarToggle?: () => void;
}

/** Responsive shell that adapts to screen size */
export interface ResponsiveShellProps {
  children: React.ReactNode;
  header?: React.ReactNode;
  sidebar?: React.ReactNode;
  footer?: React.ReactNode;
  breakpoint?: "sm" | "md" | "lg" | "xl";
}

// ============================================================================
// Content Templates
// ============================================================================

/** Browse/listing page template props */
export interface BrowseLayoutProps {
  title?: string;
  filters?: React.ReactNode;
  search?: React.ReactNode;
  sort?: React.ReactNode;
  content: React.ReactNode;
  sidebar?: React.ReactNode;
  pagination?: React.ReactNode;
  actions?: React.ReactNode;
}

/** Detail page template props */
export interface DetailLayoutProps {
  title: string;
  breadcrumbs?: React.ReactNode;
  hero?: React.ReactNode;
  content: React.ReactNode;
  sidebar?: React.ReactNode;
  actions?: React.ReactNode;
  relatedContent?: React.ReactNode;
}

/** Dashboard template props */
export interface DashboardLayoutProps {
  title: string;
  widgets: React.ReactNode[];
  sidebar?: React.ReactNode;
  quickActions?: React.ReactNode;
  notifications?: React.ReactNode;
}

// ============================================================================
// Form Templates
// ============================================================================

/** Form page template props */
export interface FormLayoutProps {
  title: string;
  subtitle?: string;
  form: React.ReactNode;
  sidebar?: React.ReactNode;
  help?: React.ReactNode;
  breadcrumbs?: React.ReactNode;
}

/** Settings page template props */
export interface SettingsLayoutProps {
  title: string;
  navigation: React.ReactNode;
  content: React.ReactNode;
  actions?: React.ReactNode;
}

// ============================================================================
// Authentication Templates
// ============================================================================

/** Auth page template props */
export interface AuthLayoutProps {
  title: string;
  subtitle?: string;
  form: React.ReactNode;
  footer?: React.ReactNode;
  backgroundImage?: string;
  logo?: React.ReactNode;
}

// ============================================================================
// Error Templates
// ============================================================================

/** Error page template props */
export interface ErrorLayoutProps {
  title: string;
  message: string;
  statusCode?: number;
  actions?: React.ReactNode;
  illustration?: React.ReactNode;
}

/** Not found page template props */
export interface NotFoundLayoutProps {
  title?: string;
  message?: string;
  searchSuggestions?: React.ReactNode;
  actions?: React.ReactNode;
}
