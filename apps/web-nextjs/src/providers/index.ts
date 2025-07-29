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

// Color mode provider for hydration-safe color mode detection
export { default as ColorModeProvider } from "./ColorModeProvider";

// Theme utilities
export { default as ThemeScript } from "./ThemeScript";
