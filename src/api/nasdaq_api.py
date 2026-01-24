from dotenv import load_dotenv
load_dotenv("./.env")
from utils.fetch_data import fetch_data
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map
from utils.parse_data import parse_greeks_prices, parse_contracts
import pandas as pd
import os

max_days = float(os.environ.get("CONTRACT_DAYS_MAX"))

def add_greeks_to_contract(index: int, greeks_dict: dict, prices_dict: dict, ticker, contract: pd.DataFrame):
    for col, value in greeks_dict.items():
        ticker.df_contracts.at[index, col] = value
    for col, value in prices_dict.items():
        ticker.df_contracts.at[index, col] = value

def get_greeks(company):
    def task_function(contract):
        return fetch_greeks_for_contract(company, contract)
    
    contracts = list(company.df_contracts.itertuples())
    results = thread_map(task_function, contracts, max_workers=20, desc=f"Fetching greeks for {company.ticker}...", ascii=True, colour="#327DA0")
    
    for index, result in enumerate(results):
        if result[0] is not None and result[1] is not None:
            add_greeks_to_contract(index, result[0], result[1], company, company.df_contracts.loc[index])

def fetch_greeks_for_contract(company, contract):
    try:
        url_greeks = f"https://api.nasdaq.com/api/quote/{company.ticker}/option-chain?assetclass=stocks&recordID={contract.nasdaq_ticker}"
        data = fetch_data(url_greeks)
        greeks_dict, prices_dict = parse_greeks_prices(contract, data)
        return greeks_dict, prices_dict
    except Exception:
        return None, None  # or raise, depending on preference

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
    return data
    
def get_contract_list(ticker):
    today = datetime.now()
    today_string = today.strftime("%Y-%m-%d")[:10]
    time_from_today = (today + timedelta(max_days)).strftime("%Y-%m-%d")[:10]
    url_contracts = f"https://api.nasdaq.com/api/quote/{ticker.ticker}/option-chain?assetclass=stocks&limit=500&fromdate={today_string}&todate={time_from_today}&excode=oprac&callput=callput&money=at&type=all"
    data = fetch_data(url_contracts)
    parse_contracts(data, ticker, today)