/**
 * Authentication Components
 *
 * This module exports all components related to authentication functionality,
 * including modals, protection utilities, and permission management.
 */

// Authentication modals
export { default as LoginModal } from "./LoginModal";
export { default as SignupModal } from "./SignupModal";
export { default as SetPasswordModal } from "./SetPasswordModal";

// Protection and permission components
export { default as ProtectedRoute } from "./ProtectedRoute";
export { default as PermissionGuard } from "./PermissionGuard";

// Higher-order components
export { default as withPermission } from "./withPermission";
