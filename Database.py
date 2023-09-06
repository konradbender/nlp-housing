from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection
from datetime import datetime
from dotenv import load_dotenv
import pymongo
import os
from typing import TypedDict, List
import pandas as pd
import logging
import pinecone
from bson import ObjectId

class House(TypedDict):
    property_id : int
    location : List[float]
    location_id : int
    page_url : str
    type_id : int
    _type : str
    price : int
    price_1 : str
    city_id : int
    city : str
    province_id : int
    province : str
    baths : int
    area : str
    purpose_id : int
    _purpose : str
    bedrooms : int
    date_added : datetime
    description : str    
    def __init__(self) -> None:
        load_dotenv()
        pw = os.getenv("MONGO_DB_PW")
        
        uri = f"mongodb+srv://api-access:{pw}@cluster0.sjdrbuv.mongodb.net/?retryWrites=true&w=majority"
        # Create a new client and connect to the server
        self.client = MongoClient(uri)
        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            logging.info("Connected to MongoDB Atlas")
        except Exception as e:
            logging.error("Could not connect to MongoDB Atlas\n", e)
            return
        
        # TODO: Remove the hardcoded database and collection names
        self.col : Collection[House] = self.client["zameen-houses"]["listings-v1"]
            
            
    def find(self, query_doc = {}, limit=None):
        cursor = self.col.find(query_doc)
        if isinstance(limit, int):
            return cursor.limit(limit)
        else:
            return cursor


class PineConeWrap:
    
    def __init__(self, key, env, index) -> None:
        load_dotenv()
        pinecone.init(      
            api_key=key,      
            environment=env,      
        )      
        self._index = pinecone.Index(index, pool_threads=10)
        
    def query(self, top_k, vector, filter):
        return self._index.query(top_k=top_k, vector=vector, filter=filter)
    
    @property
    def index(self):
        return self._index
        
        
