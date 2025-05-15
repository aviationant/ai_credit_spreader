from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv("./.env")

def connect_to_db():
    client = MongoClient(os.environ.get("MONGO_URI"))
    db = client.creditSpreader

    return db

def get_db_predictions(db):
    predictions = db["predictions"]
    return list(predictions.find())


def add_db_items(db, records):
    try:
        db.predictions.insert_many(records)
    except:
        print("Failed to post to DB.")
