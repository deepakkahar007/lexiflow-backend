from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from db.client import get_db
from db.query import createUser, getUserByEmail
# from helper.auth import hash_password


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
    token: str


authRouter = APIRouter(prefix="/auth", tags=["Authentication"])


@authRouter.post("/register", name="Register User", response_model=UserRegisterResponse)
async def register(user: UserRegisterRequestBody, db: AsyncSession = Depends(get_db)):

    if not user.name or not user.email or not user.password:
        return UserRegisterResponse(status=False, message="Missing required fields")

    is_user_exists = await getUserByEmail(db, user.email)
    if is_user_exists:
        return UserRegisterResponse(status=False, message="User already exists")

    # hashed_password = hash_password(user.password)

    # saved_user = await createUser(db, user.name, user.email, hashed_password)

    # if not saved_user:
    #     return UserRegisterResponse(status=False, message="User not registered")

    return UserRegisterResponse(status=True, message="User registered successfully")


@authRouter.post("/login", name="Login User", response_model=UserLoginResponse)
async def login(user: UserLoginRequestBody):
    return UserLoginResponse(
        status=True, message="User logged in successfully", token="token"
    )
