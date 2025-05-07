/**
 * Hooks API
 *
 * This module provides a centralized export for all hooks in the application.
 * Hooks are organized by their responsibility:
 * - core: Authentication, routing, and application-wide concerns
 * - domain: Business domain operations and data handling
 * - ui: User interface and rendering concerns
 */

// Core hooks (auth, routing, etc.)
export * from "./core";

// Domain-specific hooks (movies, actors, genres, search)
export * from "./domain";

// UI-related hooks (debounce, intersection, responsiveness)
export * from "./ui";

// Note: All auth hooks are now exported from the core module
// There's no need to explicitly import them here as they're included in the core export
