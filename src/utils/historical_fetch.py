from dotenv import load_dotenv
load_dotenv("./.env")
from datetime import datetime, timedelta
from fetch_data import fetch_data
import pandas as pd
import json

import os

ticker_string = os.environ.get("TICKERS")
tickers = ticker_string.split(",")
predict_bool = os.environ.get("PREDICT")

print(ticker_string)

days_ago = 30
days_before_ago = 730

def create_historical_csv(ticker):
    today = datetime.now().strftime("%Y-%m-%d")[:10]
    days_ago_format = (datetime.now() - timedelta(days_ago)).strftime("%Y-%m-%d")[:10]
    days_before_ago_format = (datetime.now() - timedelta(days_before_ago)).strftime("%Y-%m-%d")[:10]
    url_price_hist = f"https://api.nasdaq.com/api/quote/{ticker}/historical?assetclass=stocks&fromdate={days_before_ago_format}&limit=1000&todate={days_ago_format}"
    data = fetch_data(url_price_hist)

    table = json.loads(data)["data"]["tradesTable"]["rows"]

    df = pd.DataFrame.from_dict(table)
    df = df.astype(str).replace({r'[\$,"]': '', ',': ''}, regex=True)
    df.to_csv(f'./historical_data/{ticker}_historical.csv', encoding='utf-8', index=False)

for ticker in tickers:
    create_historical_csv(ticker)