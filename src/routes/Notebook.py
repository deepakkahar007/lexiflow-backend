from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from db.client import DbSession
from db.query import (
    createNotebook,
    deleteNotebookById,
    getAllNotebooks,
    getDocumentsByNotebookId,
    getUserNotebooksById,
)
from error.decorator import handle_errors
from error.exceptions import NotFoundException

notebookRoute = APIRouter(prefix="/notebook", tags=["Notebook"])


class BaseResponseClass(BaseModel):
    status: bool
    message: str | None
    count: int


class NotebookCreateRequest(BaseModel):
    user_id: UUID
    name: str
    description: str


class NotebookResponse(BaseModel):
    status: bool
    id: UUID | None
    message: str | None
    error: Annotated[str | None, "Error message"]


class AllNoteBooks(BaseModel):
    id: UUID
    name: str
    description: str
    user_id: UUID

    model_config = {"from_attributes": True}


class GetNotebookByIdResponse(BaseModel):
    id: UUID
    name: str
    description: str
    user_id: UUID

    model_config = {"from_attributes": True}


class GetNotebookByUserId(BaseModel):
    id: UUID
    name: str
    description: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotebookByUserIdResponse(BaseResponseClass):
    notebook: list[GetNotebookByUserId]


@notebookRoute.get("/all", response_model=list[AllNoteBooks])
@handle_errors(default_error_message="Failed to get all notebooks")
async def get_all_notebooks(db: DbSession):
    result = await getAllNotebooks(session=db)
    return result


@notebookRoute.post("/create", response_model=NotebookResponse)
@handle_errors(default_error_message="Failed to create notebook")
async def create_notebook(payload: NotebookCreateRequest, db: DbSession):
    notebook = await createNotebook(
        session=db,
        user_id=payload.user_id,
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


@notebookRoute.get("/documents/{id}")
@handle_errors(not_found_message="No documents found for this notebook")
async def get_documents_by_notebook_id(id: str, db: DbSession):
    result = await getDocumentsByNotebookId(session=db, notebook_id=id)
    return result


@notebookRoute.get("/user/{id}", response_model=NotebookByUserIdResponse)
@handle_errors(default_error_message="No notebooks found for this user")
async def get_notebooks_by_user_id(id: str, db: DbSession):
    result = await getUserNotebooksById(session=db, user_id=id)

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


@notebookRoute.get("/{id}", response_model=list[GetNotebookByIdResponse])
@handle_errors(not_found_message="No notebooks found for this user")
async def get_notebook_by_user_id(id: str, db: DbSession):
    result = await getUserNotebooksById(session=db, user_id=id)
    return result


@notebookRoute.delete("/{id}")
@handle_errors()
async def delete_notebook(id: str, db: DbSession):
    result = await deleteNotebookById(session=db, id=id)
    return result
