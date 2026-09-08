from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from db.client import DbSession
from db.query import (
    createNotebook,
    deleteNotebookById,
    getAllNotebooks,
    getUserNotebooksById,
)

notebookRoute = APIRouter(prefix="/notebook", tags=["Notebook"])


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

    model_config = {"from_attributes": True}


class GetNotebookByIdResponse(BaseModel):
    id: UUID
    name: str
    description: str

    model_config = {"from_attributes": True}


@notebookRoute.get("/all", response_model=list[AllNoteBooks])
async def get_all_notebooks(db: DbSession):
    result = await getAllNotebooks(session=db)
    return result


@notebookRoute.post("/create")
async def create_notebook(payload: NotebookCreateRequest, db: DbSession):
    try:
        notebook = await createNotebook(
            session=db,
            user_id=payload.user_id,
            name=payload.name,
            description=payload.description,
        )

        print("-" * 50)
        print(notebook)
        print("-" * 50)

        if not notebook:
            return NotebookResponse(
                status=False,
                id=None,
                message="Failed to create notebook",
                error="Notebook not created",
            )

        return NotebookResponse(
            status=True,
            id=notebook,
            message="Notebook created successfully",
            error=None,
        )
    except Exception as e:
        return NotebookResponse(status=False, id=None, message=str(e), error=str(e))


@notebookRoute.get("/{id}", response_model=list[GetNotebookByIdResponse])
async def get_notebook_by_user_id(id: str, db: DbSession):

    result = await getUserNotebooksById(session=db, user_id=id)

    return result


@notebookRoute.delete("/{id}")
async def delete_notebook(id: str, db: DbSession):
    result = await deleteNotebookById(session=db, id=id)
    return result
