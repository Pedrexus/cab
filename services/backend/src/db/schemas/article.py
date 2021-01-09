from uuid import UUID, uuid4

from pydantic import BaseModel, PositiveInt, Field


class Article(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    body: str

