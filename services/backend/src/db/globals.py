from asonic import Client
from asonic.enums import Channel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import declarative_base

from core.settings import DATABASE_URL, SONIC_URL, SONIC_PORT, SONIC_PASSWORD, SONIC_MAX_CONNECTIONS, SONIC_COLLECTION


def sonic_factory():
    return Client(host=SONIC_URL, port=SONIC_PORT, password=SONIC_PASSWORD, max_connections=SONIC_MAX_CONNECTIONS)


class Database:
    engine = create_async_engine(str(DATABASE_URL))
    sonic = sonic_factory()
    BaseTable = declarative_base()

    @classmethod
    async def connect(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(cls.BaseTable.metadata.drop_all)
            await conn.run_sync(cls.BaseTable.metadata.create_all)

        await cls.sonic.channel(Channel.INGEST)
        await cls.sonic.flushc(SONIC_COLLECTION)

    @classmethod
    async def disconnect(cls):
        await cls.engine.dispose()
