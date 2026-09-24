from uuid import UUID

from pydantic import BaseModel


class DocumentResponseSchema(BaseModel):
    id: UUID
    notebook_id: UUID
    original_filename: str
    processed_filename: str
    file_path: str
    mime_type: str
    status: str

    class Config:
        from_attributes = True


class DocumentListByNotebookId(BaseModel):
    id: UUID
    notebook_id: UUID
    original_filename: str
    status: str

    class Config:
        from_attributes = True
