import itertools
import json
UNIQUE_KEY = "property_id"
from pprint import pprint
from typing import List

import Database
from Database import PineConeWrap
import importlib 
importlib.reload(Database)
from dotenv import load_dotenv
load_dotenv()
import os




def chunks(iterable, batch_size=100):
    """A helper function to break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = list(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = list(itertools.islice(it, batch_size))
        
def generate_entry(path):
    with open(path, "r") as f:
        for line in f:
            doc =  json.loads(line)
            rest_of_data = doc.copy()
            for key in ("Ada-Embedding", UNIQUE_KEY):
                rest_of_data.pop(key)
            if not isinstance(doc[UNIQUE_KEY], int):
                continue
            if not isinstance(doc["Ada-Embedding"], list):
                continue
            if len(doc["Ada-Embedding"]) != 1536:
                continue
            result = (
                str(doc[UNIQUE_KEY]),
                doc["Ada-Embedding"],
                rest_of_data
            )
            yield result

if __name__ == '__main__':

    env = os.environ("PINECONE_ENV")
    index = os.environ("PINCEONE_INDEX")
    key = os.environ("PINECONE_KEY")

    col = PineConeWrap(key, env, index)

    async_results = [
        col.index.upsert(vectors=ids_vectors_chunk, async_req=True)
        for ids_vectors_chunk in chunks(generate_entry("/Users/konrad/code/fun/nlp-housing/data/complete-data.jsonl"), 100)
    ]
    # Wait for and retrieve responses (this raises in case of error)
    [async_result.get() for async_result in async_results]