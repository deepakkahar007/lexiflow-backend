from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

T = TypeVar("T")


class DBErrorHandler:
    """Centralized database error handling configuration"""

    def __init__(self):
        self.error_handlers: dict[type, Callable] = {
            IntegrityError: self._handle_integrity_error,
            SQLAlchemyError: self._handle_sqlalchemy_error,
        }

    def _handle_integrity_error(self, error: IntegrityError, func_name: str) -> str:
        """Handle integrity constraint violations"""
        print(f"Integrity constraint violation in {func_name}: {error}")
        return "integrity_error"

    def _handle_sqlalchemy_error(self, error: SQLAlchemyError, func_name: str) -> str:
        """Handle general SQLAlchemy errors"""
        print(f"Database operation failed in {func_name}: {error}")
        return "database_error"

    def _handle_generic_error(self, error: Exception, func_name: str) -> str:
        """Handle unexpected errors"""
        print(f"Unexpected error in {func_name}: {error}")
        return "unexpected_error"


# Global instance
error_handler = DBErrorHandler()


def handle_db_errors(
    default_return: Any = None, log_errors: bool = True, raise_on_error: bool = False
):
    """
    Enhanced global decorator with custom error handling.

    Args:
        default_return: Value to return on error
        log_errors: Whether to log errors
        raise_on_error: Whether to raise custom exceptions instead of returning defaults
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_type = type(e)
                handler = error_handler.error_handlers.get(
                    error_type, error_handler._handle_generic_error
                )

                if log_errors:
                    handler(e, func.__name__)

                if raise_on_error:
                    raise

                return default_return

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_type = type(e)
                handler = error_handler.error_handlers.get(
                    error_type, error_handler._handle_generic_error
                )

                if log_errors:
                    handler(e, func.__name__)

                if raise_on_error:
                    raise

                return default_return

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# from collections.abc import Callable
# from functools import wraps
# from typing import Any, TypeVar

# from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# T = TypeVar("T")


# def handle_db_errors(default_return: Any = None, log_errors: bool = True):
#     """
#     Global decorator for handling database errors consistently.

#     Args:
#         default_return: Value to return on error (None, [], etc.)
#         log_errors: Whether to log errors (can be disabled for tests)
#     """

#     def decorator(func: Callable[..., T]) -> Callable[..., T]:
#         @wraps(func)
#         async def async_wrapper(*args: Any, **kwargs: Any) -> T:
#             try:
#                 return await func(*args, **kwargs)
#             except IntegrityError as e:
#                 if log_errors:
#                     print(f"Integrity error in {func.__name__}: {e}")
#                 return default_return
#             except SQLAlchemyError as e:
#                 if log_errors:
#                     print(f"Database error in {func.__name__}: {e}")
#                 return default_return
#             except Exception as e:
#                 # Catch unexpected errors but log them distinctly
#                 if log_errors:
#                     print(f"Unexpected error in {func.__name__}: {e}")
#                 return default_return

#         @wraps(func)
#         def sync_wrapper(*args: Any, **kwargs: Any) -> T:
#             try:
#                 return func(*args, **kwargs)
#             except IntegrityError as e:
#                 if log_errors:
#                     print(f"Integrity error in {func.__name__}: {e}")
#                 return default_return
#             except SQLAlchemyError as e:
#                 if log_errors:
#                     print(f"Database error in {func.__name__}: {e}")
#                 return default_return
#             except Exception as e:
#                 if log_errors:
#                     print(f"Unexpected error in {func.__name__}: {e}")
#                 return default_return

#         # Return appropriate wrapper based on whether function is async
#         import asyncio

#         if asyncio.iscoroutinefunction(func):
#             return async_wrapper
#         else:
#             return sync_wrapper

#     return decorator
