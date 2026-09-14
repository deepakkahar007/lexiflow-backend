from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError

from db.client import DbSession
from db.query import createUser, getAllUsers, getUserByEmail
from helper.auth import create_access_token, hash_password, verify_password


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


class UserListResponse(BaseModel):
    id: UUID
    email: EmailStr
    is_verified: bool
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
        extra = "ignore"


authRouter = APIRouter(prefix="/auth", tags=["Authentication"])


@authRouter.post("/register", name="Register User", response_model=UserRegisterResponse)
async def register(user: UserRegisterRequestBody, db: DbSession):
    try:
        if not user.name or not user.email or not user.password:
            return UserRegisterResponse(status=False, message="Missing required fields")

        is_user_exists = await getUserByEmail(db, user.email)
        if is_user_exists:
            return UserRegisterResponse(status=False, message="User already exists")

        hashed_password = hash_password(user.password)

        saved_user = await createUser(db, user.name, user.email, hashed_password)

        if not saved_user:
            return UserRegisterResponse(status=False, message="User not registered")

        return UserRegisterResponse(status=True, message="User registered successfully")

    except Exception as e:
        return UserRegisterResponse(status=False, message=str(e))


@authRouter.post("/login", name="Login User", response_model=UserLoginResponse)
async def login(user: UserLoginRequestBody, db: DbSession, response: Response):
    try:
        if not user.email or not user.password:
            return UserLoginResponse(status=False, message="Missing required fields")

        is_user_exists = await getUserByEmail(db, user.email)

        if not is_user_exists:
            return UserLoginResponse(status=False, message="User not found")

        is_password_valid = verify_password(user.password, is_user_exists.password)

        if not is_password_valid:
            return UserLoginResponse(status=False, message="Invalid password")

        token = create_access_token(
            {
                "id": str(is_user_exists.id),
                "name": is_user_exists.name,
                "email": is_user_exists.email,
            }
        )

        response.set_cookie(
            key="access_token",
            value=token,
            httponly=False,
            secure=True,
            samesite="none",
            max_age=1800,
        )

        return UserLoginResponse(
            status=True,
            message=f"{is_user_exists.name} logged in successfully",
        )
    except (ValueError, IntegrityError) as e:
        print(e)
        return UserLoginResponse(status=False, message="Something went wrong")


@authRouter.post("/logout", name="Logout User", response_model=UserLogoutResponse)
async def logout(response: Response):
    try:
        response.delete_cookie(
            key="access_token",
            httponly=False,
            secure=True,
            samesite="none",
        )

        return UserLogoutResponse(status=True, message="Logged out successfully")
    except (ValueError, IntegrityError) as e:
        return UserRegisterResponse(status=False, message=str(e))


@authRouter.get("/users/list", response_model=list[UserListResponse])
async def get_users_list(db: DbSession):
    users = await getAllUsers(db)
    return users


# @authRouter.get("/profile")
# async def get_profile(current_user: CurrentUser) -> UserResponse:
#     return UserResponse.model_validate(current_user)
