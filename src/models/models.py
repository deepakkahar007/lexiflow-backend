from sqlalchemy import Boolean, String, true
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseDatabaseModel


class DocumentTable(BaseDatabaseModel):
    __tablename__ = "documents"

    name: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)


class UserTable(BaseDatabaseModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=True, default=True, server_default=true()
    )
