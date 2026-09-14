import shutil
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import UploadFile

# Dynamically resolve project root: moves up from helper file location to root uploads folder
UPLOAD_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "uploads"
CHUNK_SIZE = 1024 * 1024  # 1MB


async def save_files_storage(files: UploadFile) -> str:
    """
    Save a file to storage.
    Returns:
        str: The generated folder ID.
    Raises:
        OSError: If the storage operation fails.
        ValueError: If the filename is invalid.
    """
    folder_name = str(uuid4())
    folder_path = UPLOAD_ROOT / folder_name
    try:
        folder_path.mkdir(parents=True, exist_ok=False)
        safe_filename = Path(files.filename).name
        if not safe_filename:
            raise ValueError("Invalid filename")
        file_path = folder_path / safe_filename
        async with aiofiles.open(file_path, "wb") as buffer:
            while chunk := await files.read(CHUNK_SIZE):
                await buffer.write(chunk)
        return folder_name
    except OSError:
        if folder_path.exists():
            try:
                shutil.rmtree(folder_path)
            except OSError:
                pass
        raise
    finally:
        await files.close()


async def get_files_storage(folder_id: str) -> list[Path]:
    """
    Get all file paths inside a stored folder ID.
    """
    folder_path = UPLOAD_ROOT / folder_id
    if not folder_path.is_dir():
        return []
    return [file for file in folder_path.iterdir() if file.is_file()]


async def add_files_to_folder(id: str, files: UploadFile) -> bool:
    """
    Add files to an existing folder.
    Returns False if the folder does not exist or saving fails.
    """

    folder_path = UPLOAD_ROOT / id

    if not folder_path.is_dir():
        return False

    safe_filename = Path(files.filename).name
    if not safe_filename:
        return False

    file_path = folder_path / safe_filename

    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            while chunk := await files.read(CHUNK_SIZE):
                await buffer.write(chunk)

        return True

    except OSError:
        return False

    finally:
        await files.close()


# import shutil
# from pathlib import Path
# from uuid import uuid4

# import aiofiles
# from fastapi import UploadFile

# UPLOAD_ROOT = Path("uploads")
# CHUNK_SIZE = 1024 * 1024  # 1MB


# async def save_files_storage(files: UploadFile) -> str:
#     """
#     Save a file to storage.
#     Returns:
#         str: The generated folder ID.
#     Raises:
#         OSError: If the storage operation fails.
#         ValueError: If the filename is invalid.
#     """
#     folder_name = str(uuid4())
#     folder_path = UPLOAD_ROOT / folder_name
#     try:
#         folder_path.mkdir(parents=True, exist_ok=False)
#         safe_filename = Path(files.filename).name
#         if not safe_filename:
#             raise ValueError("Invalid filename")
#         file_path = folder_path / safe_filename
#         async with aiofiles.open(file_path, "wb") as buffer:
#             while chunk := await files.read(CHUNK_SIZE):
#                 await buffer.write(chunk)
#         return folder_name
#     except OSError:
#         if folder_path.exists():
#             try:
#                 shutil.rmtree(folder_path)
#             except OSError:
#                 pass
#         raise
#     finally:
#         await files.close()


# async def get_files_storage():
#     """
#     Get files from storage
#     """
#     pass


# async def add_files_to_folder(id: str, files: UploadFile) -> bool:
#     """
#     Add files to an existing folder.
#     Returns False if the folder does not exist or saving fails.
#     """

#     folder_path = UPLOAD_ROOT / id

#     if not folder_path.is_dir():
#         return False

#     safe_filename = Path(files.filename).name
#     file_path = folder_path / safe_filename

#     try:
#         async with aiofiles.open(file_path, "wb") as buffer:
#             while chunk := await files.read(CHUNK_SIZE):
#                 await buffer.write(chunk)

#         return True

#     except OSError:
#         return False

#     finally:
#         await files.close()
