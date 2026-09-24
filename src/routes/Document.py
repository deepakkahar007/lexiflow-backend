from fastapi import APIRouter, UploadFile

from config.celery import celery_client
from db.client import DbSession
from db.query import createDocument, getAllDocuments, getDocumentsByNotebookId
from error.decorator import handle_errors
from helper.storage import add_files_to_folder, save_files_storage
from schema.responseSchema import DocumentListByNotebookId, DocumentResponseSchema

documentRouter = APIRouter(prefix="/document", tags=["Document"])


# @documentRouter.get("/test")
# @handle_errors(default_error_message="Failed to create tasks")
# async def test():

#     task = celery_client.send_task("src.celery.add", args=[2, 25])
#     # task = celery_client.send_task("src.celery.hello", args=["johnny boi"])

#     return {"message": "Document test endpoint", "task": task.id}


@documentRouter.post("/upload")
@handle_errors(default_error_message="Failed to upload files")
async def upload_files(files: UploadFile, db: DbSession) -> dict[str, str | bool]:

    folder_id = await save_files_storage(files)

    if not folder_id:
        return {"status": False, "error": "Failed to save file"}

    # Create document record in database
    documet_id = await createDocument(
        db,
        id=folder_id,
        notebook_id="bf906298-12b3-4c67-ae95-f4fc4be1a953",
        filename=files.filename,
        type=files.headers.get("content-type") or "application/pdf",
        file_size=files.size or 0,
    )

    if not documet_id:
        return {"status": False, "error": "Failed to create document record"}

    task = celery_client.send_task(
        "src.celery.process_uploaded_document", args=[documet_id]
    )

    if not task:
        return {"status": False, "error": "Failed to create task"}

    return {"status": True, "id": task.id}


@documentRouter.post("/upload/{id}")
@handle_errors(default_error_message="Failed to upload files to folder")
async def upload_files_to_folder(id: str, files: UploadFile) -> dict[str, str | bool]:

    file_uploaded = await add_files_to_folder(id, files)

    if not file_uploaded:
        return {"status": False, "error": "Failed to upload file"}

    return {"status": True, "message": "File uploaded successfully"}


@documentRouter.get("/documents/all", response_model=list[DocumentResponseSchema])
@handle_errors(default_error_message="Failed to get documents")
async def get_documents(
    db: DbSession,
) -> list[DocumentResponseSchema]:

    doc = await getAllDocuments(db)
    return doc


@documentRouter.get("/list/{id}", response_model=list[DocumentListByNotebookId] | None)
@handle_errors(default_error_message="Failed to get documents")
async def get_documents_by_notebook_id(
    id: str,
    db: DbSession,
) -> list[DocumentListByNotebookId] | None:

    doc = await getDocumentsByNotebookId(db, id)

    if not doc:
        return None

    return doc
