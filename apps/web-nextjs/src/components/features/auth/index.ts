/**
 * Authentication Components
 *
 * This module exports all components related to authentication functionality,
 * including modals, protection utilities, and permission management.
 */

// ============================================================================
// Types
// ============================================================================

export type {
  // Auth modal types from local types file
  AuthModalBaseProps,
  LoginModalProps,
  SignupModalProps,
  SetPasswordModalProps,
  PermissionGuardProps,
  ProtectedRouteProps,
  AuthFormValidation,
} from "./types";

// ============================================================================
// Components
// ============================================================================

// Authentication modals
export { default as LoginModal } from "./LoginModal";
export { default as SignupModal } from "./SignupModal";
export { default as SetPasswordModal } from "./SetPasswordModal";

// Protection and permission components
export { default as ProtectedRoute } from "./ProtectedRoute";
export { default as PermissionGuard } from "./PermissionGuard";

// Higher-order components
export { default as withPermission } from "./withPermission";
