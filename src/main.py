from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from config.settings import config
from helper.storage import save_files_storage

origins = ["http://localhost:5173"]

app = FastAPI()

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
