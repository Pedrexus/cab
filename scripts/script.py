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
filename = "data.parquet"
batch_size = 50

df = pd.read_parquet(filename)

for i in tqdm(df.index[::batch_size]):
    batch = df.iloc[i:i + batch_size].to_dict("records")
    r = requests.post(uri, json=batch)
    if r.status_code != 200:
        print(f"error: {r.status_code}")
    
