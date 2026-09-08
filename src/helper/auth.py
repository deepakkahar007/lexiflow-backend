from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from config.settings import config
from db.client import DbSession
from db.query import getUserById
from schema import User

pwd_context = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> Annotated[str | None]:
    try:
        return jwt.encode(data, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    except InvalidTokenError as e:
        print(e)
        return None


def decode_token(token: str) -> Annotated[dict | None]:
    try:
        return jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
    except InvalidTokenError as e:
        print(e)
        return None


def verify_user_decorator(token: str):
    pass


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbSession,
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)

        user_id = payload.get("sub")

        if not isinstance(user_id, str):
            raise credentials_exception

    except jwt.PyJWTError as exc:
        raise credentials_exception from exc

    user = await getUserById(db, user_id)

    if user is None:
        raise credentials_exception

    return user


CurrentUser = Annotated["User", Depends(get_current_user)]
