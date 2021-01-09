from typing import Optional, List

from asonic import Client
from asonic.enums import Channel

from db.globals import Database

from .. import schemas, tables
from sqlalchemy.ext.asyncio import AsyncSession


class ArticleRepository:

    def __init__(self):
        self.engine = Database.engine
        self.sonic = Client(host='sonichost', port=1491, password='SecretPassword', max_connections=100)

    async def push_node(self, article: tables.Article):
        # insert into sonic - inside sql session
        await self.sonic.channel(Channel.INGEST)
        status = await self.sonic.push('collection', 'bucket', str(article.id), f'{article.title} {article.body}')
        return {"article": article, "status": status}

    async def create(self, article: schemas.Article):
        obj = tables.Article(**article.dict())

        # insert into db
        async with AsyncSession(self.engine) as session:
            async with session.begin():
                session.add(obj)
                response = await self.push_node(obj)
            await session.commit()

            print("obj id", obj.id)

        return response

    async def list(self):
        # db list
        async with AsyncSession(self.engine) as session:
             await session.run_sync(lambda s: s.query(tables.Article).all())

    async def count(self):
        # db count
        async with AsyncSession(self.engine) as session:
            return await session.run_sync(lambda s: s.query(tables.Article).count())

    async def get(self, pk: Optional[int] = None):
        async with AsyncSession(self.engine) as session:
            return await session.run_sync(
                lambda s: s.query(tables.Article).filter(tables.Article.id == pk).first()
            )

    async def find(self, question: str):
        """finds the context id using sonic and grabs the data from the db"""
        id_array = await self.sonic.query('collection', 'bucket', question)
        if id_array:
            pk = int(id_array[0].decode('utf-8'))
            return await self.get(pk)

    async def batch_create(self, articles: List[schemas.Article]):
        async with AsyncSession(self.engine) as session:
            async with session.begin():
                items = []
                for a in articles:
                    obj = tables.Article(**a.dict())
                    await self.sonic.push('collection', 'bucket', str(obj.id), f'{a.title} {a.body}')
                    items.append(obj)
                session.add_all(items)
            await session.commit()
        return len(articles)
