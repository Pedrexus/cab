from sqlalchemy import Column, Integer, String

from ..globals import Database


class Article(Database.BaseTable):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(String)




