/**
 * UI Component Types - Legacy File (DEPRECATED)
 *
 * ⚠️ THIS FILE IS DEPRECATED AND WILL BE REMOVED ⚠️
 *
 * All types have been moved to their appropriate atomic levels:
 * - Basic types: `./atoms/types.ts`
 * - Molecule types: `./molecules/types.ts`
 * - Organism types: `./organisms/types.ts`
 * - Template types: `./templates/types.ts`
 *
 * ✅ MIGRATION COMPLETE:
 * - [x] ToggleIconButton → uses atoms/types
 * - [x] BaseModal → uses organisms/types
 * - [x] FormInput → uses molecules/types
 * - [x] InfoBanner → uses molecules/types
 * - [x] SortSelector → uses molecules/types
 * - [x] MovieBrowseLayout → uses templates/types
 * - [x] AppShell → uses templates/types
 * - [x] ResponsiveShell → uses templates/types
 *
 * 🚨 DO NOT ADD NEW TYPES HERE 🚨
 * Add them to the appropriate atomic level instead.
 *
 * This file will be deleted once all remaining components
 * have been migrated to use atomic-level types.
 */

// Temporary re-exports for backward compatibility
// These will be removed once migration is complete

export type {
  // Atoms
  ComponentSize,
  ExtendedComponentSize,
  LoadingStateProps,
  ErrorStateProps,
  VoidCallback,
  ValueCallback,
  ClickHandler,
  WithChildren,
  WithOptionalChildren,
  ThemeAwareProps,
} from "./atoms/types";

export type {
  // Molecules
  BaseFormInputProps,
  FormValidationState,
  AsyncCallback,
  ChangeHandler,
  SubmitHandler,
} from "./molecules/types";

export type {
  // Organisms
  BaseModalProps,
} from "./organisms/types";

export type {
  // Templates
  AppShellProps,
  BrowseLayoutProps,
} from "./templates/types";
