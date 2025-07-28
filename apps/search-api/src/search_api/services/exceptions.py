"""Search service exceptions."""


class SearchServiceException(Exception):
    """Exception raised when search operations fail."""

    def __init__(self, message: str, error_code: str = "SEARCH_ERROR"):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
