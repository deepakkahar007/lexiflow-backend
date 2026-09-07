import pymupdf
from docling.document_converter import DocumentConverter
from fastapi import APIRouter, UploadFile

from db.client import DbSession
from db.query import createDocument, getAllDocuments
from helper.storage import add_files_to_folder, save_files_storage
from schema.User import UserResponse

documentRouter = APIRouter(prefix="/document", tags=["Document"])


@documentRouter.post("/parse")
async def parse_document():

    # converter = DocumentConverter()
    # result = converter.convert(
    #     "/Users/deepak/Documents/projects/lexiflow_document_processing/server/uploads/4b056517ce0f46aaae20e4c08d85d138/smallpdf.pdf"
    # )

    # markdown_content = result.document.export_to_markdown()
    # return {"markdown": markdown_content}
    doc = pymupdf.open(
        "/Users/deepak/Documents/projects/lexiflow_document_processing/server/uploads/4b056517ce0f46aaae20e4c08d85d138/smallpdf.pdf"
    )  # open a document

    text = ""

    for page in doc:  # iterate the document pages
        text += page.get_text()  # get plain text (is in UTF-8)

    doc.close()

    return {"message": "Document parsed successfully", "text": text}


@documentRouter.post("/upload")
async def upload_files(files: UploadFile) -> dict[str, str | bool]:

    folder_name = await save_files_storage(files)

    return {"status": True, "id": folder_name}


@documentRouter.post("/upload/{id}")
async def upload_files_to_folder(id: str, files: UploadFile) -> dict[str, str | bool]:

    file_uploaded = await add_files_to_folder(id, files)

    if not file_uploaded:
        return {"status": False, "error": "Failed to upload file"}

    return {"status": True, "message": "File uploaded successfully"}


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
