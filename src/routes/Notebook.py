from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from db.client import DbSession
from db.query import (
    createNotebook,
    deleteNotebookById,
    getDocumentsByNotebookId,
    getOwnedNotebook,
    getUserNotebooksById,
)
from error.decorator import handle_errors
from error.exceptions import NotFoundException
from helper.auth import CurrentUser

notebookRoute = APIRouter(prefix="/notebook", tags=["Notebook"])


class BaseResponseClass(BaseModel):
    status: bool
    message: str | None
    count: int


class NotebookCreateRequest(BaseModel):
    name: str
    description: str | None = None


class NotebookResponse(BaseModel):
    status: bool
    id: UUID | None
    message: str | None
    error: Annotated[str | None, "Error message"]


class AllNoteBooks(BaseModel):
    id: UUID
    name: str
    description: str | None
    user_id: UUID

    model_config = {"from_attributes": True}


class GetNotebookByIdResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    user_id: UUID

    model_config = {"from_attributes": True}


class GetNotebookByUserId(BaseModel):
    id: UUID
    name: str
    description: str | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotebookByUserIdResponse(BaseResponseClass):
    notebook: list[GetNotebookByUserId]


def require_owned_notebook(notebook) -> None:
    """Raise 404 when the notebook is missing or belongs to another user.

    Both cases collapse to 404 so that ids cannot be probed for existence.
    """
    if notebook is None:
        raise NotFoundException(message="Notebook not found")


@notebookRoute.post("/create", response_model=NotebookResponse)
@handle_errors(default_error_message="Failed to create notebook")
async def create_notebook(
    payload: NotebookCreateRequest, db: DbSession, user: CurrentUser
):
    """Create a notebook owned by the caller. user_id is never read from the body."""
    notebook = await createNotebook(
        session=db,
        user_id=user.id,
        name=payload.name,
        description=payload.description,
    )

    if not notebook:
        raise NotFoundException(message="Failed to create notebook")

    return NotebookResponse(
        status=True,
        id=notebook,
        message="Notebook created successfully",
        error=None,
    )


@notebookRoute.get("/user/me", response_model=NotebookByUserIdResponse)
@handle_errors(default_error_message="No notebooks found for this user")
async def get_my_notebooks(db: DbSession, user: CurrentUser):
    """List the caller's notebooks. The user id comes from the session cookie."""
    result = await getUserNotebooksById(session=db, user_id=str(user.id))

    if len(result) == 0:
        return NotebookByUserIdResponse(
            status=False,
            message="No notebooks found for this user",
            count=0,
            notebook=[],
        )

    return {
        "status": True,
        "message": "Notebooks retrieved successfully",
        "count": len(result),
        "notebook": result,
    }


@notebookRoute.get("/documents/{id}")
@handle_errors(not_found_message="No documents found for this notebook")
async def get_documents_by_notebook_id(id: str, db: DbSession, user: CurrentUser):
    require_owned_notebook(await getOwnedNotebook(db, id, str(user.id)))
    result = await getDocumentsByNotebookId(
        session=db, notebook_id=id, user_id=str(user.id)
    )
    return result


@notebookRoute.get("/{id}", response_model=list[GetNotebookByIdResponse])
@handle_errors(not_found_message="No notebooks found for this user")
async def get_notebook_by_user_id(id: str, db: DbSession, user: CurrentUser):
    """Return a single notebook, scoped to the caller."""
    notebook = await getOwnedNotebook(db, id, str(user.id))
    require_owned_notebook(notebook)
    return [notebook]


@notebookRoute.delete("/{id}")
@handle_errors()
async def delete_notebook(id: str, db: DbSession, user: CurrentUser):
    """Delete a notebook owned by the caller."""
    notebook = await getOwnedNotebook(db, id, str(user.id))
    require_owned_notebook(notebook)

    deleted = await deleteNotebookById(session=db, id=id, user_id=str(user.id))

    if not deleted:
        raise NotFoundException(message="Notebook not found")

    return {"status": True, "message": "Notebook deleted successfully"}