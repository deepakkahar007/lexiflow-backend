from fastapi import APIRouter, Form, UploadFile

from config.celery import celery_client
from db.client import DbSession
from db.query import (
    createDocument,
    deleteDocumentById,
    getDocumentsByNotebookId,
    getOwnedDocument,
    getOwnedNotebook,
)
from error.decorator import handle_errors
from error.exceptions import NotFoundException
from helper.auth import CurrentUser
from helper.storage import add_files_to_folder, save_files_storage
from schema.responseSchema import DocumentListByNotebookIdResponse

documentRouter = APIRouter(prefix="/document", tags=["Document"])


@documentRouter.post("/upload")
@handle_errors(default_error_message="Failed to upload files")
async def upload_files(
    notebook_id: str,
    files: UploadFile,
    db: DbSession,
    user: CurrentUser,
) -> dict[str, str | bool]:
    """Upload a PDF into a notebook owned by the caller.

    notebook_id is a form field because which notebook to upload into cannot be
    derived from the session, but ownership is still enforced against it.
    """
    notebook = await getOwnedNotebook(db, notebook_id, str(user.id))

    if notebook is None:
        raise NotFoundException(message="Notebook not found")

    folder_id = await save_files_storage(files)

    if not folder_id:
        return {"status": False, "error": "Failed to save file"}

    document_id = await createDocument(
        db,
        id=folder_id,
        notebook_id=notebook_id,
        filename=files.filename,
        type=files.headers.get("content-type") or "application/pdf",
        file_size=files.size or 0,
    )

    if not document_id:
        return {"status": False, "error": "Failed to create document record"}

    task = celery_client.send_task(
        "src.celery.process_uploaded_document", args=[document_id]
    )

    if not task:
        return {"status": False, "error": "Failed to create task"}

    return {"status": True, "id": task.id}


@documentRouter.post("/upload/{id}")
@handle_errors(default_error_message="Failed to upload files to folder")
async def upload_files_to_folder(
    id: str,
    files: UploadFile,
    db: DbSession,
    user: CurrentUser,
) -> dict[str, str | bool]:
    """Append a file to an existing document owned by the caller."""
    document = await getOwnedDocument(db, id, str(user.id))

    if document is None:
        raise NotFoundException(message="Document not found")

    file_uploaded = await add_files_to_folder(id, files)

    if not file_uploaded:
        return {"status": False, "error": "Failed to upload file"}

    return {"status": True, "message": "File uploaded successfully"}


@documentRouter.get("/list/{id}", response_model=DocumentListByNotebookIdResponse)
@handle_errors(default_error_message="Failed to get documents")
async def get_documents_by_notebook_id(
    id: str,
    db: DbSession,
    user: CurrentUser,
) -> DocumentListByNotebookIdResponse:
    """List the documents in a notebook owned by the caller."""
    doc = await getDocumentsByNotebookId(db, id, str(user.id))

    if not doc:
        return DocumentListByNotebookIdResponse(
            status=True,
            message="No documents found",
            count=0,
            documents=[],
        )

    return DocumentListByNotebookIdResponse(
        status=True,
        message="Documents retrieved successfully",
        count=len(doc),
        documents=doc,
    )


@documentRouter.delete("/delete/{id}")
@handle_errors(default_error_message="Failed to delete document")
async def delete_document(
    id: str,
    db: DbSession,
    user: CurrentUser,
) -> dict[str, str | bool]:
    """Soft-delete a document owned by the caller."""
    document = await getOwnedDocument(db, id, str(user.id))

    if document is None:
        raise NotFoundException(message="Document not found")

    await deleteDocumentById(db, id, str(user.id))

    return {"status": True, "message": "Document deleted successfully"}