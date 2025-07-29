import { useCallback } from "react";
import { createLogger } from "@/utils/logging";

interface UseErrorHandlingOptions {
  /** Page identifier for logging */
  pageId: string;
  /** Resource ID being loaded (e.g., genreId, actorId) */
  resourceId: number | string;
  /** Resource name for logging (e.g., genreName, actorName) */
  resourceName?: string;
  /** Refetch function from React Query hook */
  refetch?: () => void;
  /** Custom retry handler */
  onRetry?: () => void;
  /** Custom back navigation handler */
  onGoBack?: () => void;
}

interface ErrorDetails {
  status?: number;
  message?: string;
  isNotFound: boolean;
  isNetworkError: boolean;
  isClientError: boolean;
}

interface UseErrorHandlingReturn {
  /** Analyzes error and returns categorized error details */
  analyzeError: (error: unknown) => ErrorDetails;
  /** Logs error with context */
  logError: (error: unknown) => void;
  /** Handler for retry actions */
  handleRetry: () => void;
  /** Handler for go back actions */
  handleGoBack: () => void;
}

/**
 * useErrorHandling - Reusable hook for consistent error handling across page components
 *
 * Provides:
 * - Error categorization (404, network, client errors)
 * - Standardized error logging
 * - Retry and navigation handlers
 * - Consistent error analysis logic
 *
 * @param options Configuration for error handling
 * @returns Error handling utilities
 */
export function useErrorHandling({
  pageId,
  resourceId,
  resourceName,
  refetch,
  onRetry,
  onGoBack,
}: UseErrorHandlingOptions): UseErrorHandlingReturn {
  const logger = createLogger(`useErrorHandling:${pageId}`);

  const analyzeError = useCallback((error: unknown): ErrorDetails => {
    const apiError = error as { status?: number; message?: string };
    const status = apiError.status;

    return {
      status,
      message: apiError.message,
      isNotFound: status === 404,
      isNetworkError: !status || status >= 500,
      isClientError:
        !!status && status >= 400 && status < 500 && status !== 404,
    };
  }, []);

  const logError = useCallback(
    (error: unknown) => {
      const errorDetails = analyzeError(error);

      logger.error(`Error in ${pageId} for resource ${resourceId}:`, {
        error,
        pageId,
        resourceId,
        resourceName,
        errorMessage: (error as Error)?.message,
        errorStatus: errorDetails.status,
        errorCategory: errorDetails.isNotFound
          ? "not_found"
          : errorDetails.isNetworkError
          ? "network_error"
          : "client_error",
      });
    },
    [pageId, resourceId, resourceName, analyzeError, logger]
  );

  const handleRetry = useCallback(() => {
    logger.info(`Retrying ${pageId} load for resource: ${resourceId}`, {
      pageId,
      resourceId,
      resourceName,
    });

    if (onRetry) {
      onRetry();
    } else if (refetch) {
      refetch();
    } else {
      logger.warn("No retry handler available");
    }
  }, [pageId, resourceId, resourceName, onRetry, refetch, logger]);

  const handleGoBack = useCallback(() => {
    logger.info(`User navigating back from ${pageId}`, {
      pageId,
      resourceId,
    });

    if (onGoBack) {
      onGoBack();
    } else if (typeof window !== "undefined") {
      if (window.history.length > 1) {
        window.history.back();
      } else {
        // Fallback to home page if no history
        window.location.href = "/";
      }
    }
  }, [pageId, resourceId, onGoBack, logger]);

  return {
    analyzeError,
    logError,
    handleRetry,
    handleGoBack,
  };
}
