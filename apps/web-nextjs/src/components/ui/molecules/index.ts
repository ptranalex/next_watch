/**
 * Molecules Index
 *
 * Export point for all molecular components and their types.
 * Molecules combine atoms to create more complex, reusable UI patterns.
 */

// ============================================================================
// Types
// ============================================================================

export type {
  BaseFormInputProps,
  FormValidationState,
  BaseFormCTAProps,
  NavLinkProps,
  SearchInputProps,
  AsyncStateProps,
  BaseCardProps,
  ExpandableContentProps,
  ContentWithActionProps,
  BannerProps,
  SortSelectorProps,
  SuggestionItemProps,
  ScrollToTopButtonProps,
  AsyncCallback,
  AsyncValueCallback,
  ChangeHandler,
  SubmitHandler,
} from "./types";

// ============================================================================
// Components
// ============================================================================

// Navigation molecules
export { default as ScrollToTopButton } from "./ScrollToTopButton";
export { default as SearchInput } from "./SearchInput";

// Data display molecules
export { default as SortSelector } from "./SortSelector";
export { default as SuggestionItem } from "./SuggestionItem";
export { default as CustomInfiniteScroll } from "./CustomInfiniteScroll";

// Feedback molecules
export { default as InfoBanner } from "./InfoBanner";
export { default as SessionExpiredModal } from "./SessionExpiredModal";
export { ErrorBoundary } from "./feedback";

// Form molecules
export { default as FormInput } from "./form/FormInput";
export { PrimaryCTA, SecondaryCTA, TertiaryCTA, Divider } from "./form/FormCTA";
export { default as FileInput } from "./form/FileInput";

// Display molecules
export { default as ExpandableText } from "./display/ExpandableText";

// Utility molecules (with prefixes to avoid naming conflicts)
export { default as MoleculeToggleIconButton } from "./ToggleIconButton";
export { default as MoleculeLoadingIndicator } from "./LoadingIndicator";
