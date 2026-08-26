from uuid import UUID

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: UUID
    name: str
    path: str
    is_active: bool

    class Config:
        from_attributes = True
