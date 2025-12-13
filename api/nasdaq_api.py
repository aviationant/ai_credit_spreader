from dotenv import load_dotenv
load_dotenv("./.env")
from utils.fetch_data import fetch_data
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from src.parse_data import parse_greeks_prices, parse_contracts
import pandas as pd
import os

max_days = float(os.environ.get("CONTRACT_DAYS_MAX"))

def add_greeks_to_contract(index: int, greeks_dict: dict, prices_dict: dict, ticker, contract: pd.DataFrame):
    for col, value in greeks_dict.items():
        ticker.df_contracts.at[index, col] = value
    for col, value in prices_dict.items():
        ticker.df_contracts.at[index, col] = value

def get_greeks_url(ticker, prediction: dict, contract: pd.DataFrame) -> str | bool:
    if ((contract.prediction >= contract.last_trade) and
        contract.call_put == "P" and
        contract.expiry_date == prediction.expiry_date):
            return f"https://api.nasdaq.com/api/quote/{ticker.ticker}/option-chain?assetclass=stocks&recordID={contract.nasdaq_ticker}"
    elif ((contract.prediction < contract.last_trade) and
        contract.call_put == "C" and
        contract.expiry_date == prediction.expiry_date):
            return f"https://api.nasdaq.com/api/quote/{ticker.ticker}/option-chain?assetclass=stocks&recordID={contract.nasdaq_ticker}"
    else: return False

def get_greeks(ticker, predict_bool):
    contracts = ticker.df_contracts
    indices = contracts.index.tolist()
    max_workers = 15
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(fetch_greeks_for_contract, ticker, row, idx): idx
            for idx, row in zip(indices, contracts.itertuples())
        }
        for future in tqdm(as_completed(future_to_index), total=len(future_to_index),
                           desc=f"Fetching Greeks for {ticker.ticker}",
                           ascii=" ░▒▓█", colour="#00FF00"):
            index, greeks_dict, prices_dict = future.result()
            if greeks_dict is not None and prices_dict is not None:
                add_greeks_to_contract(index, greeks_dict, prices_dict, ticker, contracts.loc[index])

def fetch_greeks_for_contract(ticker, contract, index):
    try:
        url_greeks = f"https://api.nasdaq.com/api/quote/{ticker.ticker}/option-chain?assetclass=stocks&recordID={contract.nasdaq_ticker}"
        data = fetch_data(url_greeks)
        greeks_dict, prices_dict = parse_greeks_prices(contract, data)
        return index, greeks_dict, prices_dict
    except Exception:
        return index, None, None  # or raise, depending on preference

def get_price_history_504(ticker):
    today = datetime.now().strftime("%Y-%m-%d")[:10]
    past_90_days = (datetime.now() - timedelta(90)).strftime("%Y-%m-%d")[:10]
    url_price_hist = f"https://api.nasdaq.com/api/quote/{ticker.ticker}/historical?assetclass=stocks&fromdate={past_90_days}&limit=100&todate={today}"
    data = fetch_data(url_price_hist)
    ticker.price_history = data

def get_price_history(ticker):
    today = datetime.now().strftime("%Y-%m-%d")[:10]
    past_90_days = (datetime.now() - timedelta(90)).strftime("%Y-%m-%d")[:10]
    url_price_hist = f"https://api.nasdaq.com/api/quote/{ticker.ticker}/historical?assetclass=stocks&fromdate={past_90_days}&limit=100&todate={today}"
    data = fetch_data(url_price_hist)
    ticker.price_history = data
    
def get_contract_list(ticker):
    today = datetime.now()
    today_string = today.strftime("%Y-%m-%d")[:10]
    time_from_today = (today + timedelta(max_days)).strftime("%Y-%m-%d")[:10]
    url_contracts = f"https://api.nasdaq.com/api/quote/{ticker.ticker}/option-chain?assetclass=stocks&limit=500&fromdate={today_string}&todate={time_from_today}&excode=oprac&callput=callput&money=at&type=all"
    data = fetch_data(url_contracts)
    parse_contracts(data, ticker, today)
    print("Fetched: ", ticker.ticker)