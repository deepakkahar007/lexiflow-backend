from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import config
from db.client import close_database, get_db
from db.query import createDocument, getAllDocuments
from helper.storage import save_files_storage
from schema.User import UserResponse

origins = ["http://localhost:5173"]


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage application startup and shutdown resources."""

    yield

    await close_database()


app = FastAPI(
    title="Async FastAPI Backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World", "res": config.PASSWORD_HASH_SECRET}


@app.post("/upload")
async def upload_files(files: UploadFile) -> dict[str, str]:

    folder_name = await save_files_storage(files)

    return {"folder_name": folder_name}


@app.get("/documents", response_model=list[UserResponse, None])
async def get_documents(
    db: AsyncSession = Depends(get_db),
) -> list[UserResponse] | None:

    doc = await getAllDocuments(db)
    return doc


@app.post("/documents")
async def create_document(
    name: str,
    path: str,
    db: AsyncSession = Depends(get_db),
):
    doc_id = await createDocument(db, name, path)
    return {"id": doc_id}
