from fastapi import APIRouter, UploadFile

from config.celery import celery_client
from db.client import DbSession
from db.query import createDocument, getAllDocuments
from error.decorator import handle_errors
from helper.storage import add_files_to_folder, save_files_storage
from schema.User import UserResponse

documentRouter = APIRouter(prefix="/document", tags=["Document"])


@documentRouter.get("/test")
@handle_errors(default_error_message="Failed to create tasks")
async def test():

    task = celery_client.send_task("src.celery.add", args=[2, 25])
    # task = celery_client.send_task("src.celery.hello", args=["johnny boi"])

    print(task)
    return {"message": "Document test endpoint", "task": task.id}


@documentRouter.post("/upload")
@handle_errors(default_error_message="Failed to upload files")
async def upload_files(files: UploadFile) -> dict[str, str | bool]:

    folder_name = await save_files_storage(files)

    task = celery_client.send_task(
        "src.celery.process_uploaded_document", args=[folder_name]
    )

    return {"status": True, "id": folder_name, "task": task.id}


@documentRouter.post("/upload/{id}")
@handle_errors(default_error_message="Failed to upload files to folder")
async def upload_files_to_folder(id: str, files: UploadFile) -> dict[str, str | bool]:

    file_uploaded = await add_files_to_folder(id, files)

    if not file_uploaded:
        return {"status": False, "error": "Failed to upload file"}

    return {"status": True, "message": "File uploaded successfully"}


@documentRouter.get("/documents", response_model=list[UserResponse, None])
@handle_errors(default_error_message="Failed to get documents")
async def get_documents(
    db: DbSession,
) -> list[UserResponse] | None:

    doc = await getAllDocuments(db)
    return doc


@documentRouter.post("/documents")
@handle_errors(default_error_message="Failed to create document")
async def create_document(
    name: str,
    path: str,
    db: DbSession,
):
    doc_id = await createDocument(db, name, path)
    return {"id": doc_id}
