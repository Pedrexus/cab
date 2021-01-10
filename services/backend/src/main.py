from typing import List

from fastapi import FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware

from core import settings
from db import schemas
from db.globals import Database
from db.repositories import QuestionAnsweringRepository, ArticleRepository

app = FastAPI(debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await Database.connect()
    # init repos


@app.on_event("shutdown")
async def shutdown():
    await Database.disconnect()


@app.post('/backup')
async def backup():
    await Database.backup()


@app.post('/restore')
async def restore():
    await Database.restore()


@app.post('/flush')
async def flush():
    await Database.flush()


@app.post('/articles')
async def add_article(article: schemas.Article):
    return await ArticleRepository().create(article)


@app.get('/articles')
async def list_all_articles():
    return await ArticleRepository().list()


@app.get('/articles/count')
async def count_all_articles():
    return await ArticleRepository().count()


@app.get('/articles/{pk}')
async def get_article(pk: str = Path(...)):
    return await ArticleRepository().get(pk)


@app.get('/find')
async def find_article(text: str):
    return await ArticleRepository().find(text)


@app.post('/articles/batch')
async def run_batch_create(articles: List[schemas.Article]):
    return await ArticleRepository().batch_create(articles)


@app.get("/ask")
async def ask_question(question: str):
    articles = await ArticleRepository().find(question)

    # build context
    context = "; ".join([f"{a.title}. {a.body}" for a in articles])
    return QuestionAnsweringRepository().answer(question, context)
