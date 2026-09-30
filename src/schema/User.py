from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class CurrentUserResponse(BaseModel):
    """The authenticated user, as returned by GET /auth/me.

    Built explicitly from the ORM row by the auth dependency rather than
    validated with from_attributes, so the shape is independent of the table.
    """

    id: UUID
    name: str
    email: EmailStr
    role: str
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Admin listing of users. Never exposed to non-privileged callers."""

    id: UUID
    email: EmailStr
    is_verified: bool
    name: str
    created_at: str

    model_config = ConfigDict(from_attributes=True, extra="ignore")