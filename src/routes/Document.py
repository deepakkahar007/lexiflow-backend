from fastapi import APIRouter, UploadFile

from db.client import DbSession
from db.query import createDocument, getAllDocuments
from helper.storage import save_files_storage
from schema.User import UserResponse

documentRouter = APIRouter(prefix="/document", tags=["Document"])


@documentRouter.post("/upload")
async def upload_files(files: UploadFile) -> dict[str, str]:

    folder_name = await save_files_storage(files)

    return {"folder_name": folder_name}


@documentRouter.get("/documents", response_model=list[UserResponse, None])
async def get_documents(
    db: DbSession,
) -> list[UserResponse] | None:

    doc = await getAllDocuments(db)
    return doc


@documentRouter.post("/documents")
async def create_document(
    name: str,
    path: str,
    db: DbSession,
):
    doc_id = await createDocument(db, name, path)
    return {"id": doc_id}
