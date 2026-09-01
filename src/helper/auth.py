from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from config.settings import config

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
