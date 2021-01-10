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
