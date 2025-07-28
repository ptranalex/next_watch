"""Enhanced error handling utilities for FastAPI applications."""

import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, Type

import httpx
from fastapi import HTTPException
from fast_core.errors.exceptions import (
    ExternalServiceException,
    ResourceNotFoundException,
    AuthenticationException,
    AuthorizationException,
    ValidationException,
    ServiceUnavailableException,
)

F = TypeVar("F", bound=Callable[..., Any])

***REMOVED*** Type alias for error mappers
ErrorMapper = Callable[[Exception], Any]
ErrorMapping = Dict[Union[Type[Exception], int, str], ErrorMapper]


def _is_expected_client_error(e: Exception) -> bool:
    """Check if an exception represents an expected client error (4xx) rather than a server error.

    Args:
        e: Exception to check

    Returns:
        True if this is an expected client error that shouldn't be logged with full stack traces
    """
    import httpx

    ***REMOVED*** Check for HTTP status errors with 4xx status codes
    if isinstance(e, httpx.HTTPStatusError):
        status_code = e.response.status_code
        ***REMOVED*** 4xx status codes are client errors - expected behavior
        return 400 <= status_code < 500

    ***REMOVED*** Check for custom client error types
    exception_name = type(e).__name__
    error_str = str(e)

    ***REMOVED*** Check if it's a client error based on the exception name or error message
    client_error_indicators = [
        "ClientError",
        "ValidationError",
        "NotFound",
        "Unauthorized",
        "Forbidden",
        "BadRequest",
        "404",
        "400",
        "401",
        "403",
    ]

    for indicator in client_error_indicators:
        if indicator in exception_name or indicator in error_str:
            return True

    return False


def handle_service_error(
    e: Exception,
    operation: str,
    service_name: str,
    logger: Any,
    preserve_semantics: bool = True,
    error_mapping: Optional[ErrorMapping] = None,
    graceful_degradation: bool = False,
    fallback_value: Any = None,
    **context: Any,
) -> Any:
    """Enhanced service error handling with semantic preservation and graceful degradation.

    Args:
        e: The exception that occurred
        operation: Description of the operation that failed
        service_name: Name of the external service
        logger: Logger instance to use
        preserve_semantics: Whether to preserve original error semantics (404 -> ResourceNotFoundException)
        error_mapping: Custom error mapping for specific exception types or status codes
        graceful_degradation: Whether to allow graceful degradation instead of raising
        fallback_value: Value to return when graceful degradation is enabled
        **context: Additional context for logging

    Returns:
        fallback_value if graceful_degradation=True, otherwise raises an exception

    Raises:
        Various exceptions based on error type and configuration when graceful_degradation=False
    """
    if graceful_degradation:
        ***REMOVED*** For graceful degradation, use info level instead of error to reduce noise
        ***REMOVED*** Try to detect if this is a structured logger (like structlog) by checking for bind method
        if hasattr(logger, "bind"):
            ***REMOVED*** Structured logging (like structlog)
            logger.info(
                f"Service error (graceful degradation): {str(e)}",
                service=service_name,
                endpoint=operation,
                exception_type=type(e).__name__,
                graceful_degradation=True,
                **context,
            )
        else:
            ***REMOVED*** Standard logging with extra
            logger.info(
                f"Service error for {operation}: {str(e)} (service={service_name}, exception_type={type(e).__name__}) - graceful degradation enabled",
                extra={
                    "service": service_name,
                    "endpoint": operation,
                    "exception_type": type(e).__name__,
                    "graceful_degradation": True,
                    **context,
                },
            )
    else:
        ***REMOVED*** Determine if this is an expected client error (like 404) or a critical server error
        is_expected_client_error = _is_expected_client_error(e)

        if is_expected_client_error:
            ***REMOVED*** For expected client errors (404, 400, etc.), use info level without stack trace
            if hasattr(logger, "bind"):
                ***REMOVED*** Structured logging (like structlog)
                logger.info(
                    f"Client error: {str(e)}",
                    service=service_name,
                    endpoint=operation,
                    exception_type=type(e).__name__,
                    expected_error=True,
                    **context,
                )
            else:
                ***REMOVED*** Standard logging with extra
                logger.info(
                    f"Client error for {operation}: {str(e)} (service={service_name}, exception_type={type(e).__name__})",
                    extra={
                        "service": service_name,
                        "endpoint": operation,
                        "exception_type": type(e).__name__,
                        "expected_error": True,
                        **context,
                    },
                )
        else:
            ***REMOVED*** For critical errors, use error level with full traceback
            if hasattr(logger, "bind"):
                ***REMOVED*** Structured logging (like structlog)
                logger.error(
                    f"Service error: {str(e)}",
                    service=service_name,
                    endpoint=operation,
                    exception_type=type(e).__name__,
                    exc_info=True,
                    **context,
                )
            else:
                ***REMOVED*** Standard logging with extra
                logger.error(
                    f"Service error for {operation}: {str(e)} (service={service_name}, exception_type={type(e).__name__})",
                    exc_info=True,
                    extra={
                        "service": service_name,
                        "endpoint": operation,
                        "exception_type": type(e).__name__,
                        **context,
                    },
                )

    ***REMOVED*** Apply custom error mapping first (highest priority)
    if error_mapping:
        mapped_exception = _apply_error_mapping(e, error_mapping, service_name)
        if mapped_exception is not None:
            if graceful_degradation:
                if hasattr(logger, "bind"):
                    ***REMOVED*** Structured logging (like structlog)
                    logger.info(
                        "Graceful degradation: returning fallback value",
                        service=service_name,
                        endpoint=operation,
                        reason="error_mapping",
                        fallback_value_type=type(fallback_value).__name__,
                    )
                else:
                    ***REMOVED*** Standard logging
                    logger.info(
                        f"Graceful degradation for {operation} in {service_name}: returning fallback value"
                    )
                return fallback_value
            raise mapped_exception

    ***REMOVED*** Handle HTTP status errors with semantic preservation
    if isinstance(e, httpx.HTTPStatusError):
        mapped_exception = _handle_http_status_error(e, service_name, preserve_semantics)
        if graceful_degradation:
            if hasattr(logger, "bind"):
                ***REMOVED*** Structured logging (like structlog)
                logger.info(
                    "Graceful degradation: returning fallback value",
                    service=service_name,
                    endpoint=operation,
                    reason="http_status_error",
                    status_code=e.response.status_code,
                    fallback_value_type=type(fallback_value).__name__,
                )
            else:
                ***REMOVED*** Standard logging
                logger.info(
                    f"Graceful degradation for {operation} in {service_name}: returning fallback value"
                )
            return fallback_value
        raise mapped_exception

    ***REMOVED*** Handle custom client errors (e.g., BackendClientPermanentError)
    if preserve_semantics:
        mapped_exception = _handle_custom_client_errors(e, service_name)
        if mapped_exception:
            if graceful_degradation:
                if hasattr(logger, "bind"):
                    ***REMOVED*** Structured logging (like structlog)
                    logger.info(
                        "Graceful degradation: returning fallback value",
                        service=service_name,
                        endpoint=operation,
                        reason="custom_client_error",
                        fallback_value_type=type(fallback_value).__name__,
                    )
                else:
                    ***REMOVED*** Standard logging
                    logger.info(
                        f"Graceful degradation for {operation} in {service_name}: returning fallback value"
                    )
                return fallback_value
            raise mapped_exception

    ***REMOVED*** Handle known exception types with semantic preservation
    if preserve_semantics:
        mapped_exception = _handle_known_exceptions(e, service_name)
        if mapped_exception:
            if graceful_degradation:
                if hasattr(logger, "bind"):
                    ***REMOVED*** Structured logging (like structlog)
                    logger.info(
                        "Graceful degradation: returning fallback value",
                        service=service_name,
                        endpoint=operation,
                        reason="known_exception",
                        fallback_value_type=type(fallback_value).__name__,
                    )
                else:
                    ***REMOVED*** Standard logging
                    logger.info(
                        f"Graceful degradation for {operation} in {service_name}: returning fallback value"
                    )
                return fallback_value
            raise mapped_exception

    ***REMOVED*** Default behavior
    if graceful_degradation:
        if hasattr(logger, "bind"):
            ***REMOVED*** Structured logging (like structlog)
            logger.info(
                "Graceful degradation: returning fallback value",
                service=service_name,
                endpoint=operation,
                reason="default_fallback",
                fallback_value_type=type(fallback_value).__name__,
            )
        else:
            ***REMOVED*** Standard logging
            logger.info(
                f"Graceful degradation for {operation} in {service_name}: returning fallback value"
            )
        return fallback_value

    ***REMOVED*** Default to service unavailable
    raise ExternalServiceException(
        detail=f"{service_name} service unavailable",
        service_name=service_name,
        error_code="SERVICE_UNAVAILABLE",
    )


def _apply_error_mapping(
    e: Exception, error_mapping: ErrorMapping, service_name: str
) -> Optional[Any]:
    """Apply custom error mapping to an exception."""

    ***REMOVED*** Check by exception type
    for error_type, mapper in error_mapping.items():
        if isinstance(error_type, type) and isinstance(e, error_type):
            return mapper(e)

    ***REMOVED*** Check by status code (if exception has one)
    if hasattr(e, "status_code"):
        status_code = getattr(e, "status_code")
        if status_code in error_mapping:
            return error_mapping[status_code](e)

    ***REMOVED*** Check by string pattern in exception message
    error_str = str(e).lower()
    for pattern, mapper in error_mapping.items():
        if isinstance(pattern, str) and pattern.lower() in error_str:
            return mapper(e)

    return None


def _handle_http_status_error(
    e: httpx.HTTPStatusError, service_name: str, preserve_semantics: bool
) -> Exception:
    """Handle HTTP status errors with optional semantic preservation."""
    status_code = e.response.status_code

    if preserve_semantics:
        if status_code == 404:
            return ResourceNotFoundException(
                detail=f"Resource not found in {service_name}",
                resource_type="Resource",
                context={"service_name": service_name, "url": str(e.request.url)},
            )
        elif status_code == 401:
            return AuthenticationException(
                detail=f"Authentication failed with {service_name}",
                context={"service_name": service_name},
            )
        elif status_code == 403:
            return AuthorizationException(
                detail=f"Access forbidden by {service_name}",
                context={"service_name": service_name},
            )
        elif status_code == 422:
            return ValidationException(
                detail=f"Validation failed in {service_name}",
                context={"service_name": service_name},
            )
        elif status_code == 503:
            return ServiceUnavailableException(
                detail=f"{service_name} service temporarily unavailable",
                service_name=service_name,
            )

    ***REMOVED*** Fallback to HTTP exceptions for other codes or when semantics not preserved
    if status_code == 401:
        return HTTPException(status_code=401, detail="Authentication failed")
    elif status_code == 404:
        return HTTPException(status_code=404, detail="Resource not found")
    elif status_code == 403:
        return HTTPException(status_code=403, detail="Access forbidden")
    elif status_code == 429:
        return HTTPException(status_code=429, detail="Rate limit exceeded")

    ***REMOVED*** Default to external service exception
    return ExternalServiceException(
        detail=f"{service_name} returned status {status_code}",
        service_name=service_name,
        upstream_status=status_code,
    )


def _handle_custom_client_errors(e: Exception, service_name: str) -> Optional[Exception]:
    """Handle custom client errors like BackendClientPermanentError."""
    exception_name = type(e).__name__
    error_str = str(e)

    ***REMOVED*** Handle BackendClientPermanentError and similar
    if "PermanentError" in exception_name or "ClientError" in exception_name:
        if "404" in error_str:
            return ResourceNotFoundException(
                detail=f"Resource not found in {service_name}",
                resource_type="Resource",
                context={"service_name": service_name, "original_error": error_str},
            )
        elif "401" in error_str:
            return AuthenticationException(
                detail=f"Authentication failed with {service_name}",
                context={"service_name": service_name, "original_error": error_str},
            )
        elif "403" in error_str:
            return AuthorizationException(
                detail=f"Access forbidden by {service_name}",
                context={"service_name": service_name, "original_error": error_str},
            )

    return None


def _handle_known_exceptions(e: Exception, service_name: str) -> Optional[Exception]:
    """Handle known exception types by preserving or enhancing them."""

    ***REMOVED*** Already semantic exceptions - enhance with service context
    if isinstance(e, ResourceNotFoundException):
        e.context = e.context or {}
        e.context["service_name"] = service_name
        return e
    elif isinstance(e, AuthenticationException):
        e.context = e.context or {}
        e.context["service_name"] = service_name
        return e
    elif isinstance(e, ValidationException):
        e.context = e.context or {}
        e.context["service_name"] = service_name
        return e

    return None


def service_error_handler(
    service_name: str,
    logger: Any,
    operation_name: Optional[str] = None,
    preserve_semantics: bool = True,
    error_mapping: Optional[ErrorMapping] = None,
    graceful_degradation: bool = False,
    fallback_value: Any = None,
    critical: bool = True,
) -> Callable[[F], F]:
    """Enhanced decorator for intelligent service error handling.

    Args:
        service_name: Name of the external service
        logger: Logger instance to use
        operation_name: Optional operation name (defaults to function name)
        preserve_semantics: Whether to preserve original error semantics (404 -> ResourceNotFoundException)
        error_mapping: Custom error mapping for specific exception types or status codes
        graceful_degradation: Whether to allow graceful degradation instead of raising
        fallback_value: Value to return when graceful degradation is enabled
        critical: Whether this operation is critical (affects error handling strategy)

    Returns:
        Decorator function

    Examples:
        ***REMOVED*** Basic usage with semantic preservation
        @service_error_handler("backend-api", logger)
        async def get_user(user_id: int):
            return await backend.get(f"/users/{user_id}")

        ***REMOVED*** Graceful degradation for non-critical features
        @service_error_handler(
            "recommendation-api",
            logger,
            graceful_degradation=True,
            fallback_value=[],
            critical=False
        )
        async def get_recommendations(user_id: int):
            return await reco.get(f"/users/{user_id}/recommendations")

        ***REMOVED*** Custom error mapping
        @service_error_handler(
            "payment-api",
            logger,
            error_mapping={
                402: lambda e: PaymentRequiredException("Insufficient funds"),
                "insufficient_funds": lambda e: PaymentRequiredException("Payment failed"),
            }
        )
        async def process_payment(amount: float):
            return await payment.post("/charge", {"amount": amount})
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                operation = operation_name or func.__name__

                ***REMOVED*** Get function signature for better context
                sig = inspect.signature(func)
                bound_args = sig.bind_partial(*args, **kwargs)
                bound_args.apply_defaults()

                ***REMOVED*** Enhanced context with function arguments
                enhanced_context = {
                    "function": func.__name__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                    "critical": critical,
                }

                ***REMOVED*** Add relevant argument values for debugging (be careful with sensitive data)
                for name, value in bound_args.arguments.items():
                    if name in ["user_id", "movie_id", "id", "limit", "page"]:  ***REMOVED*** Safe parameters
                        enhanced_context[f"arg_{name}"] = value

                result = handle_service_error(
                    e=e,
                    operation=operation,
                    service_name=service_name,
                    logger=logger,
                    preserve_semantics=preserve_semantics,
                    error_mapping=error_mapping,
                    graceful_degradation=graceful_degradation,
                    fallback_value=fallback_value,
                    **enhanced_context,
                )

                ***REMOVED*** If graceful degradation returned a value, return it
                if graceful_degradation and result is not None:
                    return result

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                operation = operation_name or func.__name__

                ***REMOVED*** Get function signature for better context
                sig = inspect.signature(func)
                bound_args = sig.bind_partial(*args, **kwargs)
                bound_args.apply_defaults()

                ***REMOVED*** Enhanced context with function arguments
                enhanced_context = {
                    "function": func.__name__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                    "critical": critical,
                }

                ***REMOVED*** Add relevant argument values for debugging (be careful with sensitive data)
                for name, value in bound_args.arguments.items():
                    if name in ["user_id", "movie_id", "id", "limit", "page"]:  ***REMOVED*** Safe parameters
                        enhanced_context[f"arg_{name}"] = value

                result = handle_service_error(
                    e=e,
                    operation=operation,
                    service_name=service_name,
                    logger=logger,
                    preserve_semantics=preserve_semantics,
                    error_mapping=error_mapping,
                    graceful_degradation=graceful_degradation,
                    fallback_value=fallback_value,
                    **enhanced_context,
                )

                ***REMOVED*** If graceful degradation returned a value, return it
                if graceful_degradation and result is not None:
                    return result

        ***REMOVED*** Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper  ***REMOVED*** type: ignore
        else:
            return sync_wrapper  ***REMOVED*** type: ignore

    return decorator


***REMOVED*** Convenience decorators for common use cases
def critical_service_handler(service_name: str, logger: Any, **kwargs: Any) -> Callable[[F], F]:
    """Decorator for critical service operations that must succeed."""
    return service_error_handler(
        service_name=service_name,
        logger=logger,
        critical=True,
        preserve_semantics=True,
        graceful_degradation=False,
        **kwargs,
    )


def optional_service_handler(
    service_name: str, logger: Any, fallback_value: Any = None, **kwargs: Any
) -> Callable[[F], F]:
    """Decorator for optional service operations that can gracefully degrade."""
    return service_error_handler(
        service_name=service_name,
        logger=logger,
        critical=False,
        preserve_semantics=True,
        graceful_degradation=True,
        fallback_value=fallback_value,
        **kwargs,
    )


def create_error_response(
    responses: Any,  ***REMOVED*** ResponseBuilder
    page: int,
    limit: int,
    collection_type: str,
    service_names: Optional[List[str]] = None,
    error_message: str = "Service unavailable",
    user_id: Optional[int] = None,
    **metadata_extras: Any,
) -> Any:
    """Create a consistent paginated error response.

    Args:
        responses: ResponseBuilder instance
        page: Page number for pagination
        limit: Items per page
        collection_type: Type of collection (e.g., "liked_movies", "top_movies")
        service_names: List of service names that were unavailable
        error_message: Error message to include
        user_id: Optional user ID for context
        **metadata_extras: Additional metadata to include

    Returns:
        Paginated response with error information
    """
    metadata = {
        "error": error_message,
        "service_info": {"aggregated_from": service_names or ["external-service"]},
        "api_version": "v1",
        "response_pattern": "paginated",
        "collection_type": collection_type,
    }

    if user_id:
        metadata["user_context"] = {"user_id": user_id}

    metadata.update(metadata_extras)

    return responses.paginated(
        items=[],
        page=page,
        limit=limit,
        total=0,
        metadata=metadata,
    )


class ServiceErrorContext:
    """Enhanced context manager for service error handling with automatic logging."""

    def __init__(
        self,
        service_name: str,
        operation: str,
        logger: Any,
        preserve_semantics: bool = True,
        graceful_degradation: bool = False,
        fallback_value: Any = None,
        **context: Any,
    ):
        self.service_name = service_name
        self.operation = operation
        self.logger = logger
        self.preserve_semantics = preserve_semantics
        self.graceful_degradation = graceful_degradation
        self.fallback_value = fallback_value
        self.context = context

    async def __aenter__(self) -> "ServiceErrorContext":
        self.logger.debug(f"Starting {self.operation} for {self.service_name}")
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        if exc_type is not None:
            result = handle_service_error(
                e=exc_val,
                operation=self.operation,
                service_name=self.service_name,
                logger=self.logger,
                preserve_semantics=self.preserve_semantics,
                graceful_degradation=self.graceful_degradation,
                fallback_value=self.fallback_value,
                **self.context,
            )

            ***REMOVED*** If graceful degradation returned a value, suppress the exception
            if self.graceful_degradation and result is not None:
                return True  ***REMOVED*** Suppress the exception

        return False  ***REMOVED*** Don't suppress the exception
