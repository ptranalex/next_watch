/**
 * UI Components Index
 *
 * Central export point for all UI components following atomic design principles.
 * Exports types, atoms, molecules, organisms, and templates.
 */

// ============================================================================
// Types (Organized by Atomic Level)
// ============================================================================

// Atom-level types (basic building blocks)
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
} from "./atoms/types";

// Molecule-level types (combined functionality)
export type {
  BaseFormInputProps,
  BaseFormCTAProps,
  FormValidationState,
  NavLinkProps,
  SearchInputProps,
  AsyncStateProps,
  BaseCardProps,
  ExpandableContentProps,
  ContentWithActionProps,
  BannerProps,
  SortSelectorProps,
  SuggestionItemProps,
  AsyncCallback,
  AsyncValueCallback,
  ChangeHandler,
  SubmitHandler,
} from "./molecules/types";

// Organism-level types (complex sections)
export type {
  BaseModalProps,
  BaseBottomSheetProps,
  BaseDrawerProps,
  NavSectionProps,
  HeaderProps,
  SectionBasedHeaderProps,
  MobileNavDrawerProps,
  ControlledMobileNavDrawerProps,
  FormOrganism,
  MultiStepFormProps,
  DataTableProps,
  ContentGridProps,
  PageHeaderProps,
} from "./organisms";

// Template-level types (page layouts)
// export type {
//   MovieBrowseLayoutProps,
//   AppShellProps,
//   ResponsiveShellProps,
// } from "./templates/types";

// ============================================================================
// Atoms
// ============================================================================

export { default as DefinitionItem } from "./atoms/display/DefinitionItem";
export { default as ColorModeSwitch } from "./atoms/ColorModeSwitch";
export { default as LoadingIndicator } from "./atoms/LoadingIndicator";
export { default as PageHeading } from "./atoms/PageHeading";
export { default as ToggleIconButton } from "./atoms/ToggleIconButton";

// Utility atoms
export { default as CopyToClipboardButton } from "./atoms/utility/CopyToClipboardButton";

// ============================================================================
// Molecules
// ============================================================================

// Layout and navigation
export { default as ScrollToTopButton } from "./molecules/ScrollToTopButton";
export { default as SortSelector } from "./molecules/SortSelector";
export { default as SuggestionItem } from "./molecules/SuggestionItem";
export { default as SearchInput } from "./molecules/SearchInput";
export { default as InfoBanner } from "./molecules/InfoBanner";
export { default as CustomInfiniteScroll } from "./molecules/CustomInfiniteScroll";
export { default as SessionExpiredModal } from "./molecules/SessionExpiredModal";

// Form molecules (named exports)
export { default as FormInput } from "./molecules/form/FormInput";
export {
  PrimaryCTA,
  SecondaryCTA,
  TertiaryCTA,
  Divider,
} from "./molecules/form/FormCTA";
export { default as FileInput } from "./molecules/form/FileInput";

// Display molecules
export { default as ExpandableText } from "./molecules/display/ExpandableText";

// Feedback molecules
export { ErrorBoundary } from "./molecules/feedback";

// Utility molecules
export { default as MoleculeToggleIconButton } from "./molecules/ToggleIconButton";
export { default as MoleculeLoadingIndicator } from "./molecules/LoadingIndicator";

// ============================================================================
// Organisms
// ============================================================================

export { default as BaseModal } from "./organisms/BaseModal";

// Navigation organisms
export { default as SideBar } from "./organisms/navigation/SideBar";
// export { default as Header } from "./organisms/navigation/Header";

// ============================================================================
// Template Components (Page Layouts)
// ============================================================================

// Template-level components (to be implemented)
// export { default as MovieBrowseLayout } from "./templates/MovieBrowseLayout";
// export { default as AppShell } from "./templates/AppShell";
// export { default as ResponsiveShell } from "./templates/ResponsiveShell";

// ============================================================================
// Legacy Type Exports (Deprecated - use atomic-level imports instead)
// ============================================================================

/**
 * @deprecated Import types from their specific atomic level instead:
 * - `./atoms/types` for basic types
 * - `./molecules/types` for molecule types
 * - `./organisms/types` for organism types
 * - `./templates/types` for template types
 */
export type {} from // Re-export all types from the main types file for backward compatibility
// This will be removed in a future version
"./types";
