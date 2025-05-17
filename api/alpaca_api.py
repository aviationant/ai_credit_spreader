from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import requests
import json
import os
import pandas as pd

ALPACA_API_ENDPOINT=os.environ.get("ALPACA_API_ENDPOINT")
ALPACA_API_KEY=os.environ.get("ALPACA_API_KEY")
ALPACA_API_SECRET=os.environ.get("ALPACA_API_SECRET")


import requests

url = "https://data.alpaca.markets/v1beta1/options/snapshots/AAPL?feed=indicative&limit=100"


headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": ALPACA_API_SECRET
}

response = requests.get(url, headers=headers)
chain = json.loads(response.text)
quote = chain.get("snapshots", {}).get("AAPL250516C00195000", {}).get("dailyBar", {})
print(quote)
# chain = chain.get("snapshots", {}).keys()
# option = chain["AAPL250516C00255000"]
# print(chain)

# for ticker in chain:
#     print(ticker)