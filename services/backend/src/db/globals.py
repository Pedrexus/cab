from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import declarative_base

from core.settings import DATABASE_URL


class Database:
    engine = create_async_engine(str(DATABASE_URL))
    BaseTable = declarative_base()

    @classmethod
    async def connect(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(cls.BaseTable.metadata.drop_all)
            await conn.run_sync(cls.BaseTable.metadata.create_all)

    @classmethod
    async def disconnect(cls):
        await cls.engine.dispose()
