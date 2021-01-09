from uuid import UUID, uuid4

from pydantic import BaseModel, PositiveInt


class Article(BaseModel):
    uuid: UUID() = uuid4()
    title: str
    body: str


class ArticleORM(Article):
    id: PositiveInt
    title: str
    body: str

    class Config:
        orm_mode = True
