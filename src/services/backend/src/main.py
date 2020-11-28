import json
import uuid
from typing import Optional

import boto3
from asonic import Client
from asonic.enums import Channel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from model import answer

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',
    aws_access_key_id="AKIAIKY4TZD5UMYM5DCA",
    aws_secret_access_key="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",
)
table = dynamodb.Table('cab')


def sonic_factory(): return Client(host='sonichost', port=1491,
                                   password='SecretPassword', max_connections=100)


class Item(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str
    body: str


@app.post("/item/")
async def create_item(item: Item):
    """ingest channel"""

    # save data in dynamo db
    table.put_item(
        Item=json.loads(item.json())
    )

    # save also in sonic
    sonic = sonic_factory()
    await sonic.channel(Channel.INGEST)
    return await sonic.push('collection', 'bucket', str(item.id), f'{item.title} - {item.body}')


@app.get("/item/")
async def get_item(string: str):
    """search channel"""
    sonic = sonic_factory()
    await sonic.channel(Channel.SEARCH)
    id_array = await sonic.query('collection', 'bucket', string)

    if id_array:
        _id = id_array[0].decode('utf-8').split(":")[-1]
        return table.get_item(
            Key={'id': _id}
        )
    return 'No match'


@app.get("/ask")
async def ask_question(question: str):
    return {"answer": question}

    sonic = sonic_factory()
    await sonic.channel(Channel.SEARCH)

    id_array = await sonic.query('collection', 'bucket', question)

    if id_array:
        _id = id_array[0].decode('utf-8').split(":")[-1]
        context = table.get_item(
            Key={'id': _id}
        )["Item"]["body"]
    else:
        context = None

    return answer(question, context)


@app.post("/batch/")
async def sync_sonic_with_db(url: str, index: str):
    """input: public url to download file
        process each line, saving in 
            sonic: id = {index}:{uuid}
            dynamodb: id = {uuid}
    """
    # TODO: pipeline must use DynamoDB Batch Writer
    pass
