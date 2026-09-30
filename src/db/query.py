from uuid import UUID

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only, selectinload

from error.databaseErrorDecorator import handle_db_errors
from models.models import DocumentTable, NotebookTable, UserTable

# NOTEBOOK QUERY


@handle_db_errors(default_return=None)
async def createNotebook(
    session: AsyncSession, user_id: UUID, name: str, description: str
):
    notebook = NotebookTable(user_id=user_id, name=name, description=description)
    session.add(notebook)
    await session.commit()
    await session.refresh(notebook)
    return notebook.id


@handle_db_errors(default_return=[])
async def getUserNotebooksById(session: AsyncSession, user_id: str):
    result = await session.execute(
        select(NotebookTable).where(
            NotebookTable.user_id == UUID(user_id),
            NotebookTable.is_deleted == False,
            NotebookTable.is_active == True,
        )
    )
    return result.scalars().all()


@handle_db_errors(default_return=[])
async def getAllNotebooks(session: AsyncSession):
    result = await session.execute(select(NotebookTable))
    return result.scalars().all()


@handle_db_errors(default_return=None)
async def getNotebookById(session: AsyncSession, id: str):
    result = await session.execute(select(NotebookTable).where(NotebookTable.id == UUID(id)))
    return result.scalars().first()


@handle_db_errors(default_return=None)
async def getOwnedNotebook(session: AsyncSession, id: str, user_id: str):
    """Fetch a notebook only when it belongs to user_id.

    Returns None both when the notebook does not exist and when it belongs to
    someone else, so the caller cannot probe for the existence of foreign ids.
    """
    result = await session.execute(
        select(NotebookTable).where(
            NotebookTable.id == UUID(id),
            NotebookTable.user_id == UUID(user_id),
            NotebookTable.is_deleted == False,
            NotebookTable.is_active == True,
        )
    )
    return result.scalars().first()


@handle_db_errors(default_return=False)
async def deleteNotebookById(
    session: AsyncSession, id: str, user_id: str | None = None
) -> bool:
    """Delete a notebook, optionally scoped to its owner.

    Scoping by user_id is what stops one user deleting another user's notebook.
    """
    statement = select(NotebookTable).where(NotebookTable.id == UUID(id))

    if user_id is not None:
        statement = statement.where(NotebookTable.user_id == UUID(user_id))

    notebook = (await session.execute(statement)).scalars().first()

    if notebook:
        await session.delete(notebook)
        await session.commit()
        return True
    return False


@handle_db_errors(default_return=[])
async def getDocumentsByNotebookId(
    session: AsyncSession, notebook_id: str, user_id: str | None = None
):
    """List documents in a notebook, optionally scoped to the notebook's owner."""
    statement = (
        select(DocumentTable)
        .options(
            load_only(
                DocumentTable.id, DocumentTable.original_filename, DocumentTable.status
            ),
            selectinload(DocumentTable.document_chunks),
        )
        .where(
            DocumentTable.notebook_id == UUID(notebook_id),
            DocumentTable.is_deleted == False,
            DocumentTable.is_active == True,
        )
    )

    if user_id is not None:
        statement = statement.join(
            NotebookTable, NotebookTable.id == DocumentTable.notebook_id
        ).where(NotebookTable.user_id == UUID(user_id))

    result = await session.execute(statement)
    return result.scalars().all()


# END OF NOTEBOOK QUERY


@handle_db_errors(default_return=None)
async def createUser(session: AsyncSession, name: str, email: str, password: str):
    user = UserTable(name=name, email=email, password=password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user.id


@handle_db_errors(default_return=None)
async def getUserByEmail(session: AsyncSession, email: str):
    result = await session.execute(select(UserTable).where(UserTable.email == email))
    return result.scalars().first()


@handle_db_errors(default_return=None)
async def getUserById(session: AsyncSession, user_id: str):
    result = await session.execute(select(UserTable).where(UserTable.id == user_id))
    return result.scalars().first()


@handle_db_errors(default_return=None)
async def updateUser(
    session: AsyncSession, user_id: int, name: str, email: str, password: str
):
    user = await getUserById(session, user_id)
    user.name = name
    user.email = email
    user.password = password
    await session.commit()
    await session.refresh(user)
    return user.id


@handle_db_errors(default_return=[])
async def getAllUsers(session: AsyncSession):
    result = await session.execute(select(UserTable))
    return result.scalars().all()


# DOCUMENT QUERY START


@handle_db_errors(default_return=None)
async def deleteDocumentById(
    session: AsyncSession, document_id: str, user_id: str | None = None
):
    """Soft-delete a document, optionally scoped to its notebook's owner.

    Scoping by user_id is what stops one user deleting another user's document.
    """
    statement = (
        update(DocumentTable)
        .where(DocumentTable.id == UUID(document_id))
        .values(is_deleted=True, is_active=False)
    )

    if user_id is not None:
        owned_notebook_ids = select(NotebookTable.id).where(
            NotebookTable.user_id == UUID(user_id)
        )
        statement = statement.where(DocumentTable.notebook_id.in_(owned_notebook_ids))

    await session.execute(statement)
    await session.commit()


@handle_db_errors(default_return=[])
async def getAllDocuments(session: AsyncSession):
    result = await session.execute(select(DocumentTable))
    return result.scalars().all()


@handle_db_errors(default_return=None)
async def getOwnedDocument(session: AsyncSession, document_id: str, user_id: str):
    """Fetch a document only when its notebook belongs to user_id.

    Returns None both when the document does not exist and when it belongs to
    someone else, so the caller cannot probe for the existence of foreign ids.
    """
    result = await session.execute(
        select(DocumentTable)
        .join(NotebookTable, NotebookTable.id == DocumentTable.notebook_id)
        .where(
            DocumentTable.id == UUID(document_id),
            NotebookTable.user_id == UUID(user_id),
            DocumentTable.is_deleted == False,
        )
    )
    return result.scalars().first()


@handle_db_errors(default_return=None)
async def createDocument(
    session: AsyncSession,
    id: str,
    notebook_id: str,
    filename: str,
    type: str,
    file_size: int,
):
    document = DocumentTable(
        id=id,
        notebook_id=notebook_id,
        original_filename=filename,
        processed_filename=filename,
        file_path=f"/uploads/{id}",
        mime_type=type,
        file_size=file_size,
        page_count=None,
        status="QUEUED",
        processing_stage=None,
        parser_version=None,
        chunker_version=None,
        embedding_provider=None,
        embedding_model=None,
        embedding_version=None,
        embedding_dimension=None,
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document.id


# DOCUMENT QUERY END
