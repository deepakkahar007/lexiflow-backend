from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, TypeVar

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .exceptions import (
    BaseAPIException,
    ConflictException,
    DatabaseException,
    NotFoundException,
    ValidationException,
)

T = TypeVar("T")


def handle_errors(
    default_error_message: str = "Operation failed",
    not_found_message: str = "Resource not found",
) -> Callable:
    """
    Decorator to automatically handle errors in route handlers.

    Usage:
        @handle_errors()
        async def my_route():
            # Your code here - no try-except needed
            pass

    The decorator will:
    - Convert database errors to proper HTTP exceptions
    - Handle validation errors
    - Convert None returns to 404 errors
    - Log all errors
    """

    def decorator(
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                result = await func(*args, **kwargs)

                # Handle None returns as 404
                if result is None:
                    raise NotFoundException(message=not_found_message)

                # Handle falsy values for success checking
                if isinstance(result, dict) and result.get("status") is False:
                    # If it's already a response with status=False, convert to exception
                    error_msg = (
                        result.get("error")
                        or result.get("message")
                        or default_error_message
                    )
                    raise BaseAPIException(
                        message=error_msg,
                        status_code=400,
                        error_code="OPERATION_FAILED",
                    )

                return result

            except IntegrityError as e:
                raise ConflictException(
                    message="Resource already exists or violates constraints",
                    details={"detail": str(e.orig)},
                )
            except SQLAlchemyError as e:
                raise DatabaseException(
                    message="Database operation failed", details={"detail": str(e)}
                )
            except ValidationError as e:
                raise ValidationException(
                    message="Validation failed", details={"errors": e.errors()}
                )
            except BaseAPIException:
                # Re-raise our custom exceptions
                raise
            except Exception as e:  # noqa: BLE001
                # Convert any other exception to internal server error
                raise BaseAPIException(
                    message=str(e) if str(e) else default_error_message,
                    status_code=500,
                    error_code="INTERNAL_ERROR",
                )

        return wrapper

    return decorator
