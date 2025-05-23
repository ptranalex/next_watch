import {
  BaseModalProps,
  ComponentSize,
  LoadingStateProps,
} from "@/components/ui/types";
import { BaseToggleProps } from "@/components/ui/atoms/types";
import { AsyncStateProps } from "@/components/ui/molecules/types";

/**
 * Mobile Component Types
 *
 * Types specific to mobile components including touch interactions,
 * mobile layouts, bottom sheets, and mobile-optimized patterns.
 */

// ============================================================================
// Touch and Gesture Patterns
// ============================================================================

/** Touch interaction props for mobile components */
export interface TouchInteractionProps {
  onTouchStart?: (event: React.TouchEvent) => void;
  onTouchEnd?: (event: React.TouchEvent) => void;
  onTouchMove?: (event: React.TouchEvent) => void;
  enableHapticFeedback?: boolean;
}

/** Swipe gesture props */
export interface SwipeGestureProps {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  swipeThreshold?: number;
}

/** Press and hold interaction props */
export interface PressHoldProps {
  onPressStart?: () => void;
  onPressEnd?: () => void;
  pressHoldDelay?: number;
  enablePressHold?: boolean;
}

// ============================================================================
// Mobile Layout Patterns
// ============================================================================

/** Mobile viewport props */
export interface MobileViewportProps {
  useSafeArea?: boolean;
  hideOnKeyboard?: boolean;
  adjustForNotch?: boolean;
}

/** Mobile container props */
export interface MobileContainerProps extends MobileViewportProps {
  fullHeight?: boolean;
  scrollable?: boolean;
  padding?: "none" | "sm" | "md" | "lg";
}

/** Mobile header props */
export interface MobileHeaderProps {
  title?: string;
  showBackButton?: boolean;
  onBackPress?: () => void;
  rightAction?: React.ReactNode;
  leftAction?: React.ReactNode;
  sticky?: boolean;
}

// ============================================================================
// Bottom Sheet and Modal Patterns
// ============================================================================

/** Mobile bottom sheet props */
export interface MobileBottomSheetProps extends BaseModalProps {
  showHandle?: boolean;
  snapPoints?: string[];
  initialSnap?: number;
  backdropDismiss?: boolean;
  swipeToClose?: boolean;
  maxHeight?: string;
}

/** Mobile form bottom sheet props */
export interface MobileFormBottomSheetProps extends MobileBottomSheetProps {
  onSubmit?: (data: Record<string, unknown>) => void;
  isSubmitting?: boolean;
  submitText?: string;
  cancelText?: string;
}

/** Mobile action sheet props */
export interface MobileActionSheetProps extends MobileBottomSheetProps {
  actions: MobileActionSheetAction[];
  destructiveIndex?: number;
  cancelIndex?: number;
}

/** Mobile action sheet action */
export interface MobileActionSheetAction {
  label: string;
  icon?: React.ElementType;
  onPress: () => void;
  isDestructive?: boolean;
  isDisabled?: boolean;
}

// ============================================================================
// Mobile Form Patterns
// ============================================================================

/** Mobile form input props */
export interface MobileFormInputProps {
  label?: string;
  placeholder?: string;
  value: string;
  onChangeText: (text: string) => void;
  error?: string;
  helpText?: string;
  keyboardType?: "default" | "numeric" | "email" | "phone";
  autoCapitalize?: "none" | "sentences" | "words" | "characters";
  autoComplete?: string;
  maxLength?: number;
  multiline?: boolean;
  numberOfLines?: number;
}

/** Mobile file input props */
export interface MobileFileInputProps {
  onFileSelect: (file: File) => void;
  accept?: string;
  multiple?: boolean;
  maxSize?: number;
  captureMode?: "camera" | "gallery" | "both";
}

/** Mobile form CTA props */
export interface MobileFormCTAProps {
  variant: "primary" | "secondary" | "tertiary";
  size?: ComponentSize;
  fullWidth?: boolean;
  isLoading?: boolean;
  loadingText?: string;
  onPress: () => void;
  children: React.ReactNode;
}

// ============================================================================
// Mobile UI Components
// ============================================================================

/** Mobile card props */
export interface MobileCardProps {
  children: React.ReactNode;
  onPress?: () => void;
  onLongPress?: () => void;
  isSelected?: boolean;
  showChevron?: boolean;
  padding?: "sm" | "md" | "lg";
}

/** Mobile action pill props */
export interface MobileActionPillProps extends BaseToggleProps {
  label: string;
  icon?: React.ElementType;
  variant?: "outline" | "filled" | "ghost";
  colorScheme?: string;
}

/** Mobile skeleton loader props */
export interface MobileSkeletonProps {
  type: "card" | "list" | "profile" | "text" | "image";
  count?: number;
  animated?: boolean;
}

/** Mobile loading indicator props */
export interface MobileLoadingProps extends LoadingStateProps {
  overlay?: boolean;
  message?: string;
  size?: "sm" | "md" | "lg";
}

// ============================================================================
// Mobile Navigation Patterns
// ============================================================================

/** Mobile tab bar props */
export interface MobileTabBarProps {
  tabs: MobileTab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  position?: "top" | "bottom";
}

/** Mobile tab definition */
export interface MobileTab {
  id: string;
  label: string;
  icon?: React.ElementType;
  badge?: string | number;
  isDisabled?: boolean;
}

/** Mobile drawer props */
export interface MobileDrawerProps extends BaseModalProps {
  position?: "left" | "right";
  width?: string;
  overlay?: boolean;
  swipeToOpen?: boolean;
  swipeToClose?: boolean;
}

// ============================================================================
// Mobile List and Grid Patterns
// ============================================================================

/** Mobile list props */
export interface MobileListProps<T = Record<string, unknown>> {
  data: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor?: (item: T, index: number) => string;
  onRefresh?: () => void;
  onEndReached?: () => void;
  refreshing?: boolean;
  loading?: boolean;
  emptyComponent?: React.ReactNode;
  headerComponent?: React.ReactNode;
  footerComponent?: React.ReactNode;
}

/** Mobile infinite scroll props */
export interface MobileInfiniteScrollProps<T = Record<string, unknown>>
  extends AsyncStateProps {
  data: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  onLoadMore: () => void;
  hasMore: boolean;
  threshold?: number;
}

/** Mobile pull to refresh props */
export interface MobilePullToRefreshProps {
  onRefresh: () => void;
  refreshing: boolean;
  refreshColor?: string;
  refreshBackgroundColor?: string;
}

// ============================================================================
// Mobile Feature Patterns
// ============================================================================

/** Mobile search props */
export interface MobileSearchProps {
  value: string;
  onChangeText: (text: string) => void;
  onSubmit?: (text: string) => void;
  placeholder?: string;
  autoFocus?: boolean;
  suggestions?: string[];
  onSuggestionPress?: (suggestion: string) => void;
  showClearButton?: boolean;
}

/** Mobile filter props */
export interface MobileFilterProps {
  filters: MobileFilter[];
  selectedFilters: string[];
  onFilterChange: (filterIds: string[]) => void;
  onReset?: () => void;
  showClearAll?: boolean;
}

/** Mobile filter definition */
export interface MobileFilter {
  id: string;
  label: string;
  icon?: React.ElementType;
  count?: number;
  isSelected?: boolean;
}

// ============================================================================
// Mobile State and Feedback Patterns
// ============================================================================

/** Mobile toast props */
export interface MobileToastProps {
  message: string;
  type?: "success" | "error" | "warning" | "info";
  duration?: number;
  position?: "top" | "bottom" | "center";
  onDismiss?: () => void;
}

/** Mobile confirmation props */
export interface MobileConfirmationProps {
  title: string;
  message?: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel?: () => void;
  type?: "default" | "destructive";
}

/** Mobile error boundary props */
export interface MobileErrorBoundaryProps {
  fallback?: React.ComponentType<{ error: Error; resetError: () => void }>;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  children: React.ReactNode;
}

// ============================================================================
// Utility Types for Mobile
// ============================================================================

/** Mobile device capabilities */
export interface MobileCapabilities {
  hasCamera?: boolean;
  hasGPS?: boolean;
  hasNotifications?: boolean;
  hasBiometrics?: boolean;
  hasVibration?: boolean;
}

/** Mobile gesture event */
export interface MobileGestureEvent {
  type: "tap" | "longPress" | "swipe" | "pinch" | "pan";
  direction?: "up" | "down" | "left" | "right";
  velocity?: number;
  distance?: number;
}
