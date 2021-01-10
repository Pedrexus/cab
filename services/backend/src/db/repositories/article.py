from typing import Optional, List

from asonic import Client
from asonic.enums import Channel
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import SONIC_COLLECTION, SONIC_BUCKET
from db.globals import Database, sonic_factory
from .. import schemas, tables


class ArticleRepository:

    def __init__(self):
        self.engine = Database.engine
        self.sonic = sonic_factory()

    async def push_node(self, article: schemas.Article):
        # insert into sonic - inside sql session
        status = await self.sonic.push(SONIC_COLLECTION, SONIC_BUCKET, str(article.uuid), f'{article.title} {article.body}')
        return {"article": article, "status": status}

    async def create(self, article: schemas.Article):
        obj = tables.Article(**article.dict())

        # insert into db
        async with AsyncSession(self.engine) as session:
            async with session.begin():
                session.add(obj)
            await session.commit()

        await self.sonic.channel(Channel.INGEST)
        return await self.push_node(article)

    async def list(self):
        async with AsyncSession(self.engine) as session:
            return await session.run_sync(lambda s: s.query(tables.Article).all())

    async def count(self):
        async with AsyncSession(self.engine) as session:
            return await session.run_sync(lambda s: s.query(tables.Article).count())

    async def get(self, pk: str):
        async with AsyncSession(self.engine) as session:
            return await session.run_sync(lambda s: s.query(tables.Article).get(pk))

    async def get_many(self, pks: List[str]):
        async with AsyncSession(self.engine) as session:
            return await session.run_sync(
                lambda s: s.query(tables.Article).filter(
                    tables.Article.uuid.in_(pks)
                ).all()
            )

    async def find(self, question: str):
        """finds the context id using sonic and grabs the data from the db"""
        await self.sonic.channel(Channel.SEARCH)
        pk_array = await self.sonic.query(SONIC_COLLECTION, SONIC_BUCKET, question)
        return await self.get_many([pk.decode('utf-8') for pk in pk_array])

    async def batch_create(self, articles: List[schemas.Article]):
        async with AsyncSession(self.engine) as session:
            async with session.begin():
                session.add_all([tables.Article(**a.dict()) for a in articles])
            await session.commit()

        await self.sonic.channel(Channel.INGEST)
        for a in articles:
            await self.push_node(a)

        return len(articles)
