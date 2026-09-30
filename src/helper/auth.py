from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from config.settings import ACCESS_TOKEN_COOKIE_NAME, config
from db.client import DbSession
from db.query import getUserById
from schema.User import CurrentUserResponse

pwd_context = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Encode a JWT payload with the configured secret and algorithm."""
    return jwt.encode(data, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT.

    Raises jwt.PyJWTError when the token is malformed, tampered with or expired so
    that callers get a 401 instead of an AttributeError on None.
    """
    return jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])


def credentials_exception(message: str = "Could not validate credentials") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_token_from_request(request: Request) -> str | None:
    """Read the access token from the auth cookie, falling back to a Bearer header.

    The cookie is the primary transport because the browser attaches it
    automatically to cross-origin requests when credentials are included.
    """
    token = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)

    if token:
        return token

    authorization = request.headers.get("Authorization")

    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip() or None

    return None


async def get_current_user(request: Request, db: DbSession) -> CurrentUserResponse:
    """Resolve the authenticated user from the request, or raise 401."""
    token = get_token_from_request(request)

    if not token:
        raise credentials_exception("Not authenticated")

    try:
        payload = decode_token(token)
    except InvalidTokenError as exc:
        raise credentials_exception() from exc

    # "sub" is the registered JWT claim for the subject. Older tokens issued before
    # this was standardised use "id", so accept both.
    raw_user_id = payload.get("sub") or payload.get("id")

    if not isinstance(raw_user_id, str):
        raise credentials_exception()

    try:
        user_id = UUID(raw_user_id)
    except ValueError as exc:
        raise credentials_exception() from exc

    user = await getUserById(db, str(user_id))

    if user is None or not user.is_active:
        raise credentials_exception()

    return CurrentUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=config.DEFAULT_USER_ROLE,
        is_verified=bool(user.is_verified),
    )


CurrentUser = Annotated[CurrentUserResponse, Depends(get_current_user)]