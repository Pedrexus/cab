import uuid
import json

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from asonic import Client
from asonic.enums import Channel
from asonic.exceptions import ClientError

import boto3

app = FastAPI()

dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1'
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

    return id_array

    if id_array:
        _id = id_array[0].decode('utf-8')
        return table.get_item(
            Key={'id': _id }
        )
    return 'No match'


@app.get("/question/")
async def ask_question(question: str): 
    print(question)

    sonic = sonic_factory()
    await sonic.channel(Channel.SEARCH)

    id_array = await sonic.query('collection', 'bucket', question)

    if id_array:
        _id = id_array[0].decode('utf-8').split(":")[-1]
        context = table.get_item(
            Key={'id': _id }
        )["Item"]["body"]
    else:
        context = None

@app.post("/batch/")
async def upload_batch(url: str, index: str)
    """input: public url to download file
        process each line, saving in 
            sonic: id = {index}:{uuid}
            dynamodb: id = {uuid}
    """
    # TODO: pipeline must use DynamoDB Batch Writer
    pass

