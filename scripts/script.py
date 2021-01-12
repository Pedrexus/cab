"""
inserts data from file into database
"""
import requests
import json
from tqdm import tqdm
from pprint import pprint
from itertools import count
import pandas as pd



uri = 'http://localhost:8000/articles/batch'

def add_large_datasets():
    filenames = ["aylien.parquet", "cord19.parquet"]
    batch_sizes = [20, 200]

    errors = 0
    for fn, bs in zip(filenames, batch_sizes):
        df = pd.read_parquet(fn)
        for i in tqdm(df.index[::bs]):
            batch = df.iloc[i:i + bs].to_dict("records")
            r = requests.post(uri, json=batch)
            if r.status_code != 200:
                errors += 1
                print(f"errors: {errors}")

def add_who_dataset():
    with open("whoint.txt", "r", encoding='utf-8') as f:
        batch = []
        for i, line in enumerate(tqdm(f)):
            if line.strip():
                body = {"title": str(i), "body": line.strip()}
                batch.append(body)
    r = requests.post(uri, json=batch)
    if r.status_code != 200:
        print(r.status_code)
        print(r.json())

if __name__ == '__main__':
    add_who_dataset()
    