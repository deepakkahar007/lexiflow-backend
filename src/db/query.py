from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import DocumentTable, UserTable


async def createUser(session: AsyncSession, name: str, email: str, password: str):
    try:
        user = UserTable(name=name, email=email, password=password)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user.id
    except Exception as e:
        print(e)
        return None


async def getUserByEmail(session: AsyncSession, email: str):
    try:
        result = await session.execute(
            select(UserTable).where(UserTable.email == email)
        )
        return result.scalars().first()
    except Exception as e:
        print(e)
        return None


async def getUserById(session: AsyncSession, user_id: int):
    try:
        result = await session.execute(select(UserTable).where(UserTable.id == user_id))
        return result.scalars().first()
    except Exception as e:
        print(e)
        return None


async def updateUser(
    session: AsyncSession, user_id: int, name: str, email: str, password: str
):
    try:
        user = await getUserById(session, user_id)
        user.name = name
        user.email = email
        user.password = password
        await session.commit()
        await session.refresh(user)
        return user.id
    except Exception as e:
        print(e)
        return None


async def getAllDocuments(session: AsyncSession):
    try:
        result = await session.execute(select(DocumentTable))
        return result.scalars().all()
    except Exception as e:
        print(e)
        return []


async def createDocument(session: AsyncSession, name: str, path: str):
    document = DocumentTable(name=name, path=path)
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document.id
