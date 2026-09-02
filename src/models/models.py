from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
    false,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseDatabaseModel


class UserTable(BaseDatabaseModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=True, default=True, server_default=true()
    )

    # Relationship to notebooks (one-to-many)
    notebooks: Mapped[list[NotebookTable]] = relationship(
        "NotebookTable", back_populates="user", cascade="all, delete-orphan"
    )


class NotebookTable(BaseDatabaseModel):
    __tablename__ = "notebooks"

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True, default=None)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=True, default=False, server_default=false()
    )

    # Relationship to user (many-to-one)
    user: Mapped[UserTable] = relationship("UserTable", back_populates="notebooks")

    # Relationship to documents (one-to-many)
    documents: Mapped[list[DocumentTable]] = relationship(
        "DocumentTable", back_populates="notebook", cascade="all, delete-orphan"
    )


class DocumentTable(BaseDatabaseModel):
    __tablename__ = "documents"

    notebook_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("notebooks.id", ondelete="CASCADE"),
        nullable=False,
    )
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    processed_filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationship to notebook (many-to-one)
    notebook: Mapped[NotebookTable] = relationship(
        "NotebookTable", back_populates="documents"
    )

    # Relationship to document pages (one-to-many)
    document_pages: Mapped[list[DocumentPagesTable]] = relationship(
        "DocumentPagesTable", back_populates="document", cascade="all, delete-orphan"
    )

    # Relationship to document chunks (one-to-many)
    document_chunks: Mapped[list[DocumentChunksTable]] = relationship(
        "DocumentChunksTable", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentPagesTable(Base):
    __tablename__ = "document_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationship to document (many-to-one)
    document: Mapped[DocumentTable] = relationship(
        "DocumentTable", back_populates="document_pages"
    )

    # Relationship to document chunks (one-to-many)
    document_chunks: Mapped[list[DocumentChunksTable]] = relationship(
        "DocumentChunksTable",
        back_populates="document_page",
        cascade="all, delete-orphan",
    )


class DocumentChunksTable(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    document_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    page_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("document_pages.id", ondelete="CASCADE"), nullable=False
    )

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    start_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    end_offset: Mapped[int] = mapped_column(Integer, nullable=False)

    search_vector: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[str] = mapped_column(Text, nullable=False)

    file_info: Mapped[str] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationship to document (many-to-one)
    document: Mapped[DocumentTable] = relationship(
        "DocumentTable", back_populates="document_chunks"
    )

    # Relationship to document page (many-to-one)
    document_page: Mapped[DocumentPagesTable] = relationship(
        "DocumentPagesTable", back_populates="document_chunks"
    )


# TODO: Add more tables as needed

# CONVERSIONS

# -------------
# id              UUID PK
# notebook_id     UUID FK → notebooks.id
# title           VARCHAR
# created_at      TIMESTAMP
# updated_at      TIMESTAMP


# MESSAGES
# id                  UUID PK
# conversation_id     UUID FK → conversations.id

# role                VARCHAR
# content             TEXT

# created_at          TIMESTAMP


# citations
# id              UUID PK
# message_id      UUID FK → messages.id
# chunk_id        UUID FK → document_chunks.id

# citation_index  INTEGER
# created_at      TIMESTAMP
