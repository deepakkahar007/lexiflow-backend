from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import UploadFile

UPLOAD_ROOT = Path("uploads")
CHUNK_SIZE = 1024 * 1024  # 1MB


async def save_files_storage(files: UploadFile) -> str:
    folder_name = uuid4().hex
    folder_path = UPLOAD_ROOT / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)

    safe_filename = Path(files.filename).name
    file_path = folder_path / safe_filename

    async with aiofiles.open(file_path, "wb") as buffer:
        while chunk := await files.read(CHUNK_SIZE):
            await buffer.write(chunk)

    await files.close()
    return folder_name


async def get_files_storage():
    pass
