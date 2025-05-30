import React from "react";
import type { PermissionGuardProps } from "./types";
import { usePermission, Permission } from "@/services/hooks";

/**
 * Component that conditionally renders children based on user permissions
 *
 * Useful for UI elements that should only be shown to users with specific permissions
 */
const PermissionGuard: React.FC<PermissionGuardProps> = ({
  requiredPermissions = [],
  children,
  fallback = null,
  redirectTo,
}) => {
  // For now, assuming single permission check - can be extended for multiple permissions
  const permission = requiredPermissions[0] as Permission;
  const { isAuthorized } = usePermission(permission);

  // If authorized, render the children
  if (isAuthorized) {
    return <>{children}</>;
  }

  // If not authorized and we have a redirect, handle it (future enhancement)
  if (redirectTo) {
    // TODO: Implement redirect logic
    console.log(`Would redirect to: ${redirectTo}`);
  }

  // Otherwise render the fallback
  return <>{fallback}</>;
};

export default PermissionGuard;
