import type { BaseModalProps } from "../../ui/types";

/**
 * Authentication Feature Types
 *
 * Types specific to authentication components including modals,
 * permissions, and form validation.
 */

// ============================================================================
// Auth Modal Types
// ============================================================================

/** Auth modal base props - shared across all auth modals */
export interface AuthModalBaseProps extends BaseModalProps {
  onSuccess?: () => void;
  redirectTo?: string;
}

/** Login modal props */
export interface LoginModalProps extends AuthModalBaseProps {
  allowSignup?: boolean;
  showForgotPassword?: boolean;
}

/** Signup modal props */
export interface SignupModalProps extends AuthModalBaseProps {
  requireEmailVerification?: boolean;
  allowLogin?: boolean;
}

/** Password modal props */
export interface SetPasswordModalProps extends AuthModalBaseProps {
  token?: string;
  email?: string;
}

// ============================================================================
// Permission & Protection Types
// ============================================================================

/** Permission guard props */
export interface PermissionGuardProps {
  children: React.ReactNode;
  requiredPermissions?: string[];
  fallback?: React.ReactNode;
  redirectTo?: string;
}

/** Protected route props */
export interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requiredRoles?: string[];
  fallback?: React.ReactNode;
}

// ============================================================================
// Form Validation Types
// ============================================================================

/** Auth form validation state - consolidated error handling */
export interface AuthFormValidation {
  email?: string;
  password?: string;
  confirmPassword?: string;
  fullName?: string;
  general?: string;
}
