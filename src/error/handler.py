import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .exceptions import BaseAPIException

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Standard error response format"""

    def __init__(
        self,
        status: bool = False,
        message: str | None = None,
        error: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        self.status = status
        self.message = message
        self.error = error
        self.error_code = error_code
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        response = {"status": self.status}
        if self.message:
            response["message"] = self.message
        if self.error:
            response["error"] = self.error
        if self.error_code:
            response["error_code"] = self.error_code
        if self.details:
            response["details"] = self.details
        return response


async def base_api_exception_handler(
    request: Request, exc: BaseAPIException
) -> JSONResponse:
    """Handle custom API exceptions"""
    logger.error(
        f"API Exception: {exc.error_code} - {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_code": exc.error_code,
            "details": exc.details,
        },
    )

    error_response = ErrorResponse(
        status=False,
        message=exc.message,
        error=exc.error_code,
        error_code=exc.error_code,
        details=exc.details,
    )

    return JSONResponse(status_code=exc.status_code, content=error_response.to_dict())


async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors"""
    logger.error(
        f"Validation Error: {exc}",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    error_response = ErrorResponse(
        status=False,
        message="Validation failed",
        error="VALIDATION_ERROR",
        error_code="VALIDATION_ERROR",
        details={"errors": exc.errors()},
    )

    return JSONResponse(status_code=422, content=error_response.to_dict())


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """Handle database integrity errors"""
    logger.error(
        f"Database Integrity Error: {exc}",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    error_response = ErrorResponse(
        status=False,
        message="Database integrity constraint violated",
        error="CONFLICT",
        error_code="CONFLICT",
        details={"detail": str(exc.orig)},
    )

    return JSONResponse(status_code=409, content=error_response.to_dict())


async def sqlalchemy_error_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """Handle general SQLAlchemy errors"""
    logger.error(
        f"Database Error: {exc}",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    error_response = ErrorResponse(
        status=False,
        message="Database operation failed",
        error="DATABASE_ERROR",
        error_code="DATABASE_ERROR",
        details={"detail": str(exc)},
    )

    return JSONResponse(status_code=500, content=error_response.to_dict())


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions"""
    logger.error(
        f"Unhandled Exception: {exc}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exc_type": type(exc).__name__,
        },
        # exc_info=True,
    )

    error_response = ErrorResponse(
        status=False,
        message="An unexpected error occurred",
        error="INTERNAL_ERROR",
        error_code="INTERNAL_ERROR",
    )

    return JSONResponse(status_code=500, content=error_response.to_dict())


def register_error_handlers(app: FastAPI) -> None:
    """Register all error handlers with the FastAPI app"""
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
