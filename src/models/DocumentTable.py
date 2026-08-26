from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseDatabaseModel


class DocumentTable(BaseDatabaseModel):
    __tablename__ = "documents"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
