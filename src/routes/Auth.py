from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

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
    token: str | None


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
async def login(user: UserLoginRequestBody, db: DbSession):
    try:
        if not user.email or not user.password:
            return UserLoginResponse(status=False, message="Missing required fields")

        is_user_exists = await getUserByEmail(db, user.email)

        if not is_user_exists:
            return UserLoginResponse(status=False, message="User not found", token=None)

        is_password_valid = verify_password(user.password, is_user_exists.password)

        if not is_password_valid:
            return UserLoginResponse(
                status=False, message="Invalid password", token=None
            )

        token = create_access_token(
            {
                "id": str(is_user_exists.id),
                "name": is_user_exists.name,
                "email": is_user_exists.email,
            }
        )

        return UserLoginResponse(
            status=True,
            message=f"{is_user_exists.name} logged in successfully",
            token=token,
        )
    except Exception as e:
        print(e)
        return UserLoginResponse(
            status=False, message="Something went wrong", token=None
        )


@authRouter.get("/users/list")
async def get_users_list(db: DbSession):
    users = await getAllUsers(db)
    return {"users": users}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@authRouter.post("/test")
async def test(user: Annotated[OAuth2PasswordRequestForm, Depends()]):

    print(user.__dict__)
    return {"status": "test"}
