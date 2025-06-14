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

def add_db_item(db, record):
    try:
        db.predictions.insert_one(record)
    except:
        print("Failed to post to DB.")

def average_duplicates():
    ticker = "AAPL"    
    db = connect_to_db()
    predictions = db["predictions"]
    docs = list(predictions.find( { "ticker": ticker } ))
    df_docs = pd.DataFrame(docs)
    expiries = {}
    
    for date in df_docs.expiry_date.unique():
        expiries[date] = []
    for index, doc in df_docs.iterrows():
        expiries[doc.expiry_date].append(doc)
    duplicates = []
    for date in expiries:
        if len(expiries[date]) > 1:
            duplicate = {
                    "date": date,
                    "prices": []
                }
            for doc in expiries[date]:
                duplicate["prices"].append(float(doc["prediction"]))
            duplicates.append(duplicate)

    for duplicate in duplicates:
        duplicate["prices"] = sum(duplicate["prices"]) / len(duplicate["prices"])
        db.predictions.delete_many( { "ticker": ticker, "expiry_date": duplicate["date"]})
        record = {
            "date": "2025-05-17",
            "current_price": 211.26,
            "ticker": ticker,
            "expiry_date": duplicate[""],
            "prediction": duplicate["rpices"]
        }
    

    add_db_item(db, record)

# average_duplicates()