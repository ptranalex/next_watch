/**
 * Providers Module
 *
 * This module exports all React context providers and their related utilities
 * for state management, theming, and responsive behavior.
 */

// Authentication provider and related utilities
export { default as AuthProvider } from "./AuthProvider";

// Responsive design provider and hook
export { ResponsiveProvider, useResponsive } from "./ResponsiveContext";

// Theme utilities
export { default as ThemeScript } from "./ThemeScript";
