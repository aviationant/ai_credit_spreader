from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv
from datetime import datetime
import requests
import json
import os

load_dotenv('./.env')
ALPACA_API_ENDPOINT=os.environ.get("ALPACA_API_ENDPOINT")
ALPACA_API_KEY=os.environ.get("ALPACA_API_KEY")
ALPACA_API_SECRET=os.environ.get("ALPACA_API_SECRET")


url = "https://data.alpaca.markets/v2/stocks/auctions?symbols=AAPL&start=2025-05-08T00%3A00%3A00Z&end=2025-05-09T00%3A00%3A00Z&limit=1000&feed=sip&sort=asc"

headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": ALPACA_API_SECRET
    }

response = requests.get(url, headers=headers)
response = json.loads(response.text, object_hook=object_hook)

print(response.auctions)