/**
 * Store Module
 *
 * This module exports all Zustand stores and their hooks for state management
 * across the application. Stores are organized by domain responsibility.
 */

// Authentication store and hook
export { useAuthStore } from "./auth";

// Movie filter store and hook
export { default as useMovieFilterStore } from "./movieFilterStore";
