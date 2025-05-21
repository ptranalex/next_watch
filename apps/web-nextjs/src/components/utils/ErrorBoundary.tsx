import React from "react";
import { createLogger } from "@/utils/logging";

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback: React.ReactNode;
  componentName?: string;
}

/**
 * Error boundary component for catching rendering errors
 * Provides a fallback UI when a component fails to render
 */
class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  { hasError: boolean }
> {
  private logger = createLogger(
    this.props.componentName
      ? `ErrorBoundary:${this.props.componentName}`
      : "ErrorBoundary"
  );

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    this.logger.error("Component error:", {
      error: error.message,
      stack: error.stack,
      componentStack: info.componentStack,
    });
  }

  render() {
    if (this.state.hasError) {
      this.logger.warn("Rendering fallback due to error");
      return this.props.fallback;
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
