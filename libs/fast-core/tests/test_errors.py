"""Tests for Fast Core error handling system.

This module tests the custom exceptions, error handlers,
and error response utilities.
"""

import pytest
from fast_core.errors.exceptions import (
    APIException,
    AuthenticationException,
    AuthorizationException,
    BusinessLogicException,
    ConflictException,
    ExternalServiceException,
    RateLimitException,
    ResourceNotFoundException,
    ServiceUnavailableException,
    ValidationException,
)
from fast_core.errors.handlers import (
    api_exception_handler,
    authentication_exception_handler,
    authorization_exception_handler,
    get_exception_handlers,
    not_found_exception_handler,
    validation_exception_handler,
)
from fast_core.errors.responses import (
    STANDARD_RESPONSES,
    ErrorDetail,
    ValidationErrorDetail,
    create_error_response,
    create_paginated_response,
    create_success_response,
    create_validation_error_response,
)
from fastapi.responses import JSONResponse


class TestAPIException:
    """Test APIException base class."""

    def test_basic_api_exception(self):
        """Test basic API exception creation."""
        exc = APIException(
            status_code=400,
            detail="Test error",
            error_code="TEST_ERROR",
            context={"field": "value"},
        )

        assert exc.status_code == 400
        assert exc.detail == "Test error"
        assert exc.error_code == "TEST_ERROR"
        assert exc.context == {"field": "value"}

    def test_api_exception_without_optional_params(self):
        """Test API exception with minimal parameters."""
        exc = APIException(status_code=500, detail="Server error")

        assert exc.status_code == 500
        assert exc.detail == "Server error"
        assert exc.error_code is None
        assert exc.context == {}

    def test_api_exception_with_headers(self):
        """Test API exception with custom headers."""
        headers = {"X-Custom-Header": "custom-value"}
        exc = APIException(
            status_code=400,
            detail="Test error",
            headers=headers,
        )

        assert exc.headers == headers


class TestValidationException:
    """Test ValidationException."""

    def test_basic_validation_exception(self):
        """Test basic validation exception."""
        field_errors = [{"field": "name", "message": "Required field"}]
        exc = ValidationException(
            detail="Validation failed",
            field_errors=field_errors,
        )

        assert exc.status_code == 422
        assert exc.detail == "Validation failed"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.field_errors == field_errors

    def test_validation_exception_defaults(self):
        """Test validation exception with defaults."""
        exc = ValidationException()

        assert exc.status_code == 422
        assert exc.detail == "Validation error"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.field_errors == []


class TestAuthenticationException:
    """Test AuthenticationException."""

    def test_basic_authentication_exception(self):
        """Test basic authentication exception."""
        exc = AuthenticationException()

        assert exc.status_code == 401
        assert exc.detail == "Authentication required"
        assert exc.error_code == "AUTHENTICATION_REQUIRED"
        assert exc.headers == {"WWW-Authenticate": "Bearer"}

    def test_authentication_exception_with_custom_headers(self):
        """Test authentication exception with custom headers."""
        custom_headers = {"WWW-Authenticate": "Basic"}
        exc = AuthenticationException(headers=custom_headers)

        assert exc.headers == custom_headers


class TestAuthorizationException:
    """Test AuthorizationException."""

    def test_basic_authorization_exception(self):
        """Test basic authorization exception."""
        required_permissions = ["admin", "write"]
        exc = AuthorizationException(
            detail="Access denied",
            required_permissions=required_permissions,
        )

        assert exc.status_code == 403
        assert exc.detail == "Access denied"
        assert exc.error_code == "INSUFFICIENT_PERMISSIONS"
        assert exc.required_permissions == required_permissions

    def test_authorization_exception_defaults(self):
        """Test authorization exception with defaults."""
        exc = AuthorizationException()

        assert exc.status_code == 403
        assert exc.detail == "Insufficient permissions"
        assert exc.required_permissions == []


class TestResourceNotFoundException:
    """Test ResourceNotFoundException."""

    def test_basic_not_found_exception(self):
        """Test basic resource not found exception."""
        exc = ResourceNotFoundException(
            detail="User not found",
            resource_type="user",
            resource_id="123",
        )

        assert exc.status_code == 404
        assert exc.detail == "User not found"
        assert exc.error_code == "RESOURCE_NOT_FOUND"
        assert exc.resource_type == "user"
        assert exc.resource_id == "123"

    def test_not_found_exception_defaults(self):
        """Test resource not found exception with defaults."""
        exc = ResourceNotFoundException()

        assert exc.status_code == 404
        assert exc.detail == "Resource not found"
        assert exc.resource_type is None
        assert exc.resource_id is None


class TestConflictException:
    """Test ConflictException."""

    def test_basic_conflict_exception(self):
        """Test basic conflict exception."""
        conflicting_resource = {"id": 1, "name": "existing"}
        exc = ConflictException(
            detail="Resource already exists",
            conflicting_resource=conflicting_resource,
        )

        assert exc.status_code == 409
        assert exc.detail == "Resource already exists"
        assert exc.error_code == "RESOURCE_CONFLICT"
        assert exc.conflicting_resource == conflicting_resource


class TestRateLimitException:
    """Test RateLimitException."""

    def test_basic_rate_limit_exception(self):
        """Test basic rate limit exception."""
        exc = RateLimitException(
            detail="Rate limit exceeded",
            retry_after=60,
        )

        assert exc.status_code == 429
        assert exc.detail == "Rate limit exceeded"
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"
        assert exc.retry_after == 60
        assert exc.headers == {"Retry-After": "60"}

    def test_rate_limit_exception_without_retry_after(self):
        """Test rate limit exception without retry after."""
        exc = RateLimitException()

        assert exc.status_code == 429
        assert exc.retry_after is None
        assert exc.headers == {}


class TestServiceUnavailableException:
    """Test ServiceUnavailableException."""

    def test_basic_service_unavailable_exception(self):
        """Test basic service unavailable exception."""
        exc = ServiceUnavailableException(
            detail="Database is down",
            service_name="database",
            retry_after=120,
        )

        assert exc.status_code == 503
        assert exc.detail == "Database is down"
        assert exc.error_code == "SERVICE_UNAVAILABLE"
        assert exc.service_name == "database"
        assert exc.headers == {"Retry-After": "120"}


class TestBusinessLogicException:
    """Test BusinessLogicException."""

    def test_basic_business_logic_exception(self):
        """Test basic business logic exception."""
        exc = BusinessLogicException(
            detail="Insufficient funds",
            error_code="INSUFFICIENT_FUNDS",
            context={"balance": 100, "requested": 200},
        )

        assert exc.status_code == 400
        assert exc.detail == "Insufficient funds"
        assert exc.error_code == "INSUFFICIENT_FUNDS"
        assert exc.context == {"balance": 100, "requested": 200}


class TestExternalServiceException:
    """Test ExternalServiceException."""

    def test_basic_external_service_exception(self):
        """Test basic external service exception."""
        exc = ExternalServiceException(
            detail="Payment service error",
            service_name="stripe",
            upstream_status=503,
        )

        assert exc.status_code == 502
        assert exc.detail == "Payment service error"
        assert exc.error_code == "EXTERNAL_SERVICE_ERROR"
        assert exc.service_name == "stripe"
        assert exc.upstream_status == 503


class TestErrorHandlers:
    """Test error handlers."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock request object."""

        class MockRequest:
            def __init__(self):
                self.url = "http://test.com/api/test"
                self.method = "GET"

        return MockRequest()

    @pytest.mark.asyncio
    async def test_api_exception_handler(self, mock_request):
        """Test API exception handler."""
        exc = APIException(
            status_code=400,
            detail="Test error",
            error_code="TEST_ERROR",
            context={"field": "value"},
        )

        response = await api_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400

        ***REMOVED*** Note: Cannot directly access response.content in tests,
        ***REMOVED*** but we can verify the response was created correctly

    @pytest.mark.asyncio
    async def test_validation_exception_handler(self, mock_request):
        """Test validation exception handler."""
        field_errors = [{"field": "name", "message": "Required"}]
        exc = ValidationException(
            detail="Validation failed",
            field_errors=field_errors,
        )

        response = await validation_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_authentication_exception_handler(self, mock_request):
        """Test authentication exception handler."""
        exc = AuthenticationException(detail="Token expired")

        response = await authentication_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_authorization_exception_handler(self, mock_request):
        """Test authorization exception handler."""
        exc = AuthorizationException(
            detail="Admin required",
            required_permissions=["admin"],
        )

        response = await authorization_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_not_found_exception_handler(self, mock_request):
        """Test resource not found exception handler."""
        exc = ResourceNotFoundException(
            detail="User not found",
            resource_type="user",
            resource_id="123",
        )

        response = await not_found_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 404

    def test_get_exception_handlers(self):
        """Test getting exception handlers mapping."""
        handlers = get_exception_handlers()

        assert APIException in handlers
        assert ValidationException in handlers
        assert AuthenticationException in handlers
        assert AuthorizationException in handlers
        assert ResourceNotFoundException in handlers
        assert ConflictException in handlers
        assert RateLimitException in handlers
        assert ServiceUnavailableException in handlers
        assert BusinessLogicException in handlers
        assert ExternalServiceException in handlers


class TestErrorResponses:
    """Test error response utilities."""

    def test_create_error_response(self):
        """Test creating error response."""
        response = create_error_response(
            message="Test error",
            error_code="TEST_ERROR",
            details={"field": "value"},
        )

        expected = {
            "success": False,
            "message": "Test error",
            "error_code": "TEST_ERROR",
            "details": {"field": "value"},
        }

        assert response == expected

    def test_create_validation_error_response(self):
        """Test creating validation error response."""
        field_errors = [{"field": "name", "message": "Required"}]
        response = create_validation_error_response(
            message="Validation failed",
            field_errors=field_errors,
        )

        expected = {
            "success": False,
            "message": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "field_errors": field_errors,
        }

        assert response == expected

    def test_create_success_response(self):
        """Test creating success response."""
        data = {"id": 1, "name": "test"}
        response = create_success_response(
            message="Operation successful",
            data=data,
        )

        expected = {
            "success": True,
            "message": "Operation successful",
            "data": data,
        }

        assert response == expected

    def test_create_paginated_response(self):
        """Test creating paginated response."""
        data = [{"id": 1}, {"id": 2}]
        response = create_paginated_response(
            data=data,
            page=1,
            page_size=10,
            total_items=25,
        )

        expected = {
            "success": True,
            "data": data,
            "pagination": {
                "page": 1,
                "page_size": 10,
                "total_items": 25,
                "total_pages": 3,
                "has_next": True,
                "has_prev": False,
            },
        }

        assert response == expected

    def test_standard_responses(self):
        """Test standard responses dictionary."""
        assert "400" in STANDARD_RESPONSES
        assert "401" in STANDARD_RESPONSES
        assert "403" in STANDARD_RESPONSES
        assert "404" in STANDARD_RESPONSES
        assert "409" in STANDARD_RESPONSES
        assert "422" in STANDARD_RESPONSES
        assert "429" in STANDARD_RESPONSES
        assert "500" in STANDARD_RESPONSES

        ***REMOVED*** Check structure of a standard response
        response_400 = STANDARD_RESPONSES["400"]
        assert "description" in response_400
        assert "model" in response_400


class TestErrorDetail:
    """Test ErrorDetail model."""

    def test_error_detail_creation(self):
        """Test ErrorDetail model creation."""
        detail = ErrorDetail(
            message="Test error",
            error_code="TEST_ERROR",
            details={"field": "value"},
        )

        assert detail.message == "Test error"
        assert detail.error_code == "TEST_ERROR"
        assert detail.details == {"field": "value"}
        assert detail.success is False

    def test_error_detail_defaults(self):
        """Test ErrorDetail model with defaults."""
        detail = ErrorDetail(message="Test error")

        assert detail.message == "Test error"
        assert detail.error_code is None
        assert detail.details is None
        assert detail.success is False


class TestValidationErrorDetail:
    """Test ValidationErrorDetail model."""

    def test_validation_error_detail_creation(self):
        """Test ValidationErrorDetail model creation."""
        field_errors = [{"field": "name", "message": "Required"}]
        detail = ValidationErrorDetail(
            message="Validation failed",
            field_errors=field_errors,
        )

        assert detail.message == "Validation failed"
        assert detail.error_code == "VALIDATION_ERROR"
        assert detail.field_errors == field_errors
        assert detail.success is False


if __name__ == "__main__":
    pytest.main([__file__])
