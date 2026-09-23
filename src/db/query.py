from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from error.databaseErrorDecorator import handle_db_errors
from models.models import DocumentTable, NotebookTable, UserTable

# NOTEBOOK QUERY


@handle_db_errors(default_return=None)
async def createNotebook(
    session: AsyncSession, user_id: int, name: str, description: str
):
    notebook = NotebookTable(user_id=user_id, name=name, description=description)
    session.add(notebook)
    await session.commit()
    await session.refresh(notebook)
    return notebook.id


@handle_db_errors(default_return=[])
async def getUserNotebooksById(session: AsyncSession, user_id: str):
    result = await session.execute(
        select(NotebookTable).where(NotebookTable.user_id == user_id)
    )
    return result.scalars().all()


@handle_db_errors(default_return=None)
async def getAllNotebooks(session: AsyncSession):
    result = await session.execute(select(NotebookTable))
    return result.scalars().all()


@handle_db_errors(default_return=None)
async def deleteNotebookById(session: AsyncSession, id: str) -> bool:
    result = await session.execute(select(NotebookTable).where(NotebookTable.id == id))
    notebook = result.scalars().first()
    if notebook:
        await session.delete(notebook)
        await session.commit()
        return True
    return False


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


@handle_db_errors(default_return=[])
async def getAllDocuments(session: AsyncSession):
    result = await session.execute(select(DocumentTable))
    return result.scalars().all()


@handle_db_errors(default_return=None)
async def createDocument(
    session: AsyncSession, id: str, notebook_id: str, filename: str
):
    document = DocumentTable(
        id=id,
        notebook_id=notebook_id,
        original_filename=filename,
        processed_filename=filename,
        file_path=f"/uploads/{id}",
        mime_type="application/octet-stream",
        file_size=0,
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
