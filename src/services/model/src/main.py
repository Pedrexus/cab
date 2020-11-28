import os
import sys

import warnings
import json

# adds EFS Filesystem to our PYTHONPATH
sys.path.append(os.environ['EFS_PIP_PATH'])
from transformers import pipeline

# WARNING: this line downloads the BERT model SQuAD finetuned
nlp = pipeline("question-answering")


def answer(question, context):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = nlp(question=question, context=context)
        return {**result, "context": context}


def handler(event, context):
    try:
        return answer(event['question'], event['context'])
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                "Access-Control-Allow-Credentials": True
            },
            "body": json.dumps({"error": repr(e)})
        }
