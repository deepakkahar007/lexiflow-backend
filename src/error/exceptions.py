from typing import Any

from fastapi import status


class BaseAPIException(Exception):
    """Base exception for all API errors"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(message)


class BadRequestException(BaseAPIException):
    """400 Bad Request"""

    def __init__(
        self, message: str = "Bad request", details: dict[str, Any] | None = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BAD_REQUEST",
            details=details,
        )


class UnauthorizedException(BaseAPIException):
    """401 Unauthorized"""

    def __init__(
        self, message: str = "Unauthorized", details: dict[str, Any] | None = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            details=details,
        )


class ForbiddenException(BaseAPIException):
    """403 Forbidden"""

    def __init__(
        self, message: str = "Forbidden", details: dict[str, Any] | None = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
            details=details,
        )


class NotFoundException(BaseAPIException):
    """404 Not Found"""

    def __init__(
        self, message: str = "Resource not found", details: dict[str, Any] | None = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details,
        )


class ConflictException(BaseAPIException):
    """409 Conflict"""

    def __init__(
        self, message: str = "Resource conflict", details: dict[str, Any] | None = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            details=details,
        )


class ValidationException(BaseAPIException):
    """422 Validation Error"""

    def __init__(
        self, message: str = "Validation error", details: dict[str, Any] | None = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class DatabaseException(BaseAPIException):
    """500 Database Error"""

    def __init__(
        self, message: str = "Database error", details: dict[str, Any] | None = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details,
        )
