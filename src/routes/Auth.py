from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, EmailStr

from config.settings import ACCESS_TOKEN_COOKIE_NAME, config
from db.client import DbSession
from db.query import createUser, getAllUsers, getUserByEmail
from helper.auth import (
    CurrentUser,
    create_access_token,
    hash_password,
    verify_password,
)
from schema.User import UserListResponse


class UserRegisterRequestBody(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLoginRequestBody(BaseModel):
    email: EmailStr
    password: str


class UserRegisterResponse(BaseModel):
    status: bool
    message: str


class UserLoginResponse(BaseModel):
    status: bool
    message: str


class UserLogoutResponse(BaseModel):
    status: bool
    message: str


class UserSessionResponse(BaseModel):
    """Session payload consumed by the client auth store."""

    id: str
    name: str
    email: EmailStr
    role: str
    is_verified: bool


def set_session_cookie(response, token: str) -> None:
    """Attach the access token cookie.

    path="/" is mandatory: without it the cookie is scoped to the request path
    (/auth), so /notebook and /document would never receive it.
    """
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=token,
        path="/",
        httponly=False,
        secure=config.cookie_secure,
        samesite=config.cookie_samesite,
        max_age=config.JWT_EXPIRATION,
    )


def clear_session_cookie(response) -> None:
    """Remove the access token cookie.

    delete_cookie only matches on the attributes given, so these must stay in
    lockstep with set_session_cookie or the cookie survives logout.
    """
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        path="/",
        httponly=False,
        secure=config.cookie_secure,
        samesite=config.cookie_samesite,
    )


authRouter = APIRouter(prefix="/auth", tags=["Authentication"])


@authRouter.post("/register", name="Register User", response_model=UserRegisterResponse)
async def register(user: UserRegisterRequestBody, db: DbSession):
    if not user.name or not user.email or not user.password:
        return UserRegisterResponse(status=False, message="Missing required fields")

    if await getUserByEmail(db, user.email):
        return UserRegisterResponse(status=False, message="User already exists")

    saved_user = await createUser(db, user.name, user.email, hash_password(user.password))

    if not saved_user:
        return UserRegisterResponse(status=False, message="User not registered")

    return UserRegisterResponse(status=True, message="User registered successfully")


@authRouter.post("/login", name="Login User", response_model=UserLoginResponse)
async def login(user: UserLoginRequestBody, db: DbSession, response: Response):
    if not user.email or not user.password:
        return UserLoginResponse(status=False, message="Missing required fields")

    db_user = await getUserByEmail(db, user.email)

    if not db_user:
        return UserLoginResponse(status=False, message="User not found")

    if not db_user.is_active:
        return UserLoginResponse(status=False, message="Account is disabled")

    if not verify_password(user.password, db_user.password):
        return UserLoginResponse(status=False, message="Invalid password")

    # "sub" is the registered JWT claim for the subject; "id" is kept for
    # compatibility with tokens issued before the claim was standardised.
    token = create_access_token(
        {
            "sub": str(db_user.id),
            "id": str(db_user.id),
            "name": db_user.name,
            "email": db_user.email,
        }
    )

    set_session_cookie(response, token)

    return UserLoginResponse(
        status=True,
        message=f"{db_user.name} logged in successfully",
    )


@authRouter.post("/logout", name="Logout User", response_model=UserLogoutResponse)
async def logout(response: Response):
    clear_session_cookie(response)
    return UserLogoutResponse(status=True, message="Logged out successfully")


@authRouter.get("/me", name="User Session", response_model=UserSessionResponse)
async def get_me(user: CurrentUser):
    """Return the authenticated user. Raises 401 when the cookie is absent or invalid."""
    return UserSessionResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
        role=user.role,
        is_verified=user.is_verified,
    )


@authRouter.get(
    "/users/list",
    response_model=list[UserListResponse],
    dependencies=[Depends(CurrentUser)],
)
async def get_users_list(db: DbSession):
    return await getAllUsers(db)