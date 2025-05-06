import React from "react";
import { usePermission, Permission } from "@/hooks";

interface PermissionGuardProps {
  /** The permission required to display the children */
  permission: Permission;

  /** Content to render when permission is granted */
  children: React.ReactNode;

  /** Optional fallback to display when permission is not granted */
  fallback?: React.ReactNode;

  /** Skip rendering altogether if no permission */
  renderNothing?: boolean;
}

/**
 * Component that conditionally renders children based on user permissions
 *
 * Useful for UI elements that should only be shown to users with specific permissions
 */
const PermissionGuard: React.FC<PermissionGuardProps> = ({
  permission,
  children,
  fallback = null,
  renderNothing = false,
}) => {
  const { isAuthorized } = usePermission(permission);

  // If authorized, render the children
  if (isAuthorized) {
    return <>{children}</>;
  }

  // If not authorized and we should render nothing, return null
  if (renderNothing) {
    return null;
  }

  // Otherwise render the fallback
  return <>{fallback}</>;
};

export default PermissionGuard;
