import React, { memo } from "react";

interface ErrorAction {
  label: string;
  onClick: () => void;
  variant?: "primary" | "secondary";
  disabled?: boolean;
}

interface ErrorStateDisplayProps {
  /** Error title */
  title: string;
  /** Error description */
  description: string;
  /** Optional additional error details */
  details?: string;
  /** Action buttons */
  actions?: ErrorAction[];
  /** Custom icon or illustration */
  icon?: React.ReactNode;
  /** Additional CSS classes */
  className?: string;
}

const buttonStyles = {
  primary:
    "px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-blue-300 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
  secondary:
    "px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 disabled:bg-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2",
};

/**
 * ErrorStateDisplay - Reusable error state component
 *
 * Provides consistent error UI across the application with:
 * - Customizable title and description
 * - Optional error details for debugging
 * - Configurable action buttons
 * - Consistent styling and accessibility
 *
 * @param props Error display configuration
 */
const ErrorStateDisplay = memo(
  ({
    title,
    description,
    details,
    actions = [],
    icon,
    className = "",
  }: ErrorStateDisplayProps) => {
    return (
      <div className={`text-center py-10 ${className}`}>
        {icon && <div className="mb-4 flex justify-center">{icon}</div>}

        <h2 className="text-xl font-semibold mb-4 text-gray-900">{title}</h2>

        <p className="text-gray-600 mb-4 max-w-md mx-auto">{description}</p>

        {details && (
          <p className="text-sm text-gray-500 mb-6 max-w-lg mx-auto">
            {details}
          </p>
        )}

        {actions.length > 0 && (
          <div className="flex justify-center space-x-4">
            {actions.map((action, index) => (
              <button
                key={index}
                onClick={action.onClick}
                disabled={action.disabled}
                className={buttonStyles[action.variant || "primary"]}
              >
                {action.label}
              </button>
            ))}
          </div>
        )}
      </div>
    );
  }
);

ErrorStateDisplay.displayName = "ErrorStateDisplay";

export default ErrorStateDisplay;
