from sqlalchemy import Column, Integer, String

from ..globals import Database


class Article(Database.BaseTable):
    __tablename__ = "articles"

    uuid = Column(String, primary_key=True, index=True)
    title = Column(String)
    body = Column(String)




