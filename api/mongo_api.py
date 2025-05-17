from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.database import Database
import pandas as pd
import os

def connect_to_db():
    client: MongoClient = MongoClient(os.environ.get("MONGO_URI"))
    db: Database = client.creditSpreader
    return db

def get_db_predictions(db, ticker):
    predictions = db["predictions"]
    return list(predictions.find( { "ticker": ticker.ticker }))

def add_db_items(db, records):
    try:
        db.predictions.insert_many(records)
    except:
        print("Failed to post to DB.")
