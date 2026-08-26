from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.DocumentTable import DocumentTable


async def getAllDocuments(session: AsyncSession):
    result = await session.execute(select(DocumentTable))
    return result.scalars().all()


async def createDocument(session: AsyncSession, name: str, path: str):
    document = DocumentTable(name=name, path=path)
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document.id
