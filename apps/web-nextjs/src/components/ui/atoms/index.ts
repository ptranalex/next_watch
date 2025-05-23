/**
 * Atoms Index
 *
 * Export point for all atomic components and their types.
 * Atoms are the basic building blocks that cannot be broken down further.
 */

// ============================================================================
// Types
// ============================================================================

export type {
  ComponentSize,
  ExtendedComponentSize,
  ResponsiveBreakpoints,
  BaseToggleProps,
  IconButtonBaseProps,
  SkeletonProps,
  BaseBadgeProps,
  LoadingStateProps,
  ErrorStateProps,
  VoidCallback,
  ValueCallback,
  ClickHandler,
  WithChildren,
  WithOptionalChildren,
  ThemeAwareProps,
} from "./types";

// ============================================================================
// Components
// ============================================================================

// Display atoms
export { default as DefinitionItem } from "./display/DefinitionItem";

// Interactive atoms
export { default as ColorModeSwitch } from "./ColorModeSwitch";
export { default as ToggleIconButton } from "./ToggleIconButton";

// Feedback atoms
export { default as LoadingIndicator } from "./LoadingIndicator";

// Layout atoms
export { default as PageHeading } from "./PageHeading";

// Utility atoms
export { default as CopyToClipboardButton } from "./utility/CopyToClipboardButton";
