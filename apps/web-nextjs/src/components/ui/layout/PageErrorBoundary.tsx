import React, { memo } from "react";
import PageLayout from "./PageLayout";
import MovieBrowseLayout from "./MovieBrowseLayout";
import ErrorStateDisplay from "../feedback/ErrorStateDisplay";
import { useErrorHandling } from "@/services/hooks";

interface PageErrorBoundaryProps {
  /** Error object from React Query or other sources */
  error?: unknown;
  /** Page identifier for logging */
  pageId: string;
  /** Resource ID being loaded */
  resourceId: number | string;
  /** Resource name for context */
  resourceName?: string;
  /** Refetch function from React Query */
  refetch?: () => void;
  /** Page title element for layout */
  title: React.ReactNode;
  /** Children to render when no error */
  children: React.ReactNode;
  /** Custom error messages */
  errorMessages?: {
    notFound?: {
      title: string;
      description: string;
    };
    client?: {
      title: string;
      description: string;
    };
  };
  /** Whether to use MovieBrowseLayout (for browse pages) or generic PageLayout (for errors) */
  useGenericLayout?: boolean;
}

/**
 * PageErrorBoundary - Reusable error handling wrapper for page components
 *
 * Provides two layout options:
 * 1. PageLayout (default) - Clean layout without controls (industry standard for errors)
 * 2. MovieBrowseLayout - Full browse layout (only when useGenericLayout=false)
 *
 * Industry Standard:
 * - Error states should use clean layouts without interactive controls
 * - Browse controls (search, sort, filter) are irrelevant when page fails
 * - Matches how YouTube, GitHub, Netflix handle error states
 *
 * Provides:
 * - Consistent error UI across pages
 * - Categorized error handling (404, client errors)
 * - Standardized retry and navigation actions
 * - Appropriate layout choice based on context
 * - Network errors bubble up to app-level error.tsx
 *
 * Usage:
 * ```tsx
 * // For error states (recommended - clean layout)
 * <PageErrorBoundary error={error} pageId="genre-page" ...>
 *   <YourPageContent />
 * </PageErrorBoundary>
 *
 * // For browse pages (only when content is functional)
 * <PageErrorBoundary useGenericLayout={false} ...>
 *   <WorkingBrowseContent />
 * </PageErrorBoundary>
 * ```
 */
const PageErrorBoundary = memo(
  ({
    error,
    pageId,
    resourceId,
    resourceName,
    refetch,
    title,
    children,
    errorMessages,
    useGenericLayout = true, // Default to clean layout for errors (industry standard)
  }: PageErrorBoundaryProps) => {
    const { analyzeError, logError, handleRetry, handleGoBack } =
      useErrorHandling({
        pageId,
        resourceId,
        resourceName,
        refetch,
      });

    // If no error, render children
    if (!error) {
      return <>{children}</>;
    }

    // Analyze and log the error
    const errorDetails = analyzeError(error);
    logError(error);

    // Choose appropriate layout component
    const LayoutComponent = useGenericLayout ? PageLayout : MovieBrowseLayout;

    // Default error messages (removed network - handled at app level)
    const messages = {
      notFound: {
        title: "Resource Not Found",
        description:
          "The resource you're looking for doesn't exist or has been removed.",
        ...errorMessages?.notFound,
      },
      client: {
        title: "Unable to Load Resource",
        description: "There was a problem loading this resource.",
        ...errorMessages?.client,
      },
    };

    // Render error based on type
    if (errorDetails.isNotFound) {
      return (
        <LayoutComponent title={title}>
          <ErrorStateDisplay
            title={messages.notFound.title}
            description={messages.notFound.description}
            actions={[
              {
                label: "Go Back",
                onClick: handleGoBack,
                variant: "primary",
              },
            ]}
          />
        </LayoutComponent>
      );
    }

    // Network errors should bubble up to app-level error boundary
    if (errorDetails.isNetworkError) {
      throw error; // Let app-level error.tsx handle this
    }

    // Client error or generic error (4xx except 404)
    return (
      <LayoutComponent title={title}>
        <ErrorStateDisplay
          title={messages.client.title}
          description={messages.client.description}
          details={
            errorDetails.message ? `Error: ${errorDetails.message}` : undefined
          }
          actions={[
            {
              label: "Try Again",
              onClick: handleRetry,
              variant: "primary",
            },
            {
              label: "Go Back",
              onClick: handleGoBack,
              variant: "secondary",
            },
          ]}
        />
      </LayoutComponent>
    );
  }
);

PageErrorBoundary.displayName = "PageErrorBoundary";

export default PageErrorBoundary;
