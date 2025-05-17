from utils.fetch_data import fetch_data
from datetime import datetime, timedelta
from tqdm import tqdm
from src.parse_data import parse_greeks_prices, parse_contracts
import pandas as pd

def add_greeks_to_contract(index: int, greeks_dict: dict, prices_dict: dict, ticker, contract: pd.DataFrame):
    for col, value in greeks_dict.items():
        ticker.df_contracts.at[index, col] = value
    for col, value in prices_dict.items():
        ticker.df_contracts.at[index, col] = value

def get_greeks_url(ticker, prediction: dict, contract: pd.DataFrame) -> str | bool:
    if ((prediction.prediction >= contract.last_trade) and
        contract.call_put == "P" and
        contract.expiry_date == prediction.expiry_date):
            return f"https://api.nasdaq.com/api/quote/{ticker.ticker}/option-chain?assetclass=stocks&recordID={contract.nasdaq_ticker}"
    elif ((prediction < contract.last_trade) and
        contract.call_put == "C" and
        contract.expiry_date == prediction.expiry_date):
            return f"https://api.nasdaq.com/api/quote/{ticker}/option-chain?assetclass=stocks&recordID={contract.nasdaq_ticker}"
    else: return False

def get_greeks(ticker, prediction: dict):
    for index, contract in tqdm(ticker.df_contracts.iterrows(), total=len(ticker.df_contracts), desc=f"Fetching Greeks for {ticker}"):
        url_greeks = get_greeks_url(ticker, prediction, contract)
        if url_greeks:
            data = fetch_data(url_greeks)
        if data:
            greeks_dict, prices_dict = parse_greeks_prices(contract, data)
            add_greeks_to_contract(index, greeks_dict, prices_dict, ticker, contract)

def get_price_history(ticker):
    today = datetime.now().strftime("%Y-%m-%d")[:10]
    past_90_days = (datetime.now() - timedelta(90)).strftime("%Y-%m-%d")[:10]
    url_price_hist = f"https://api.nasdaq.com/api/quote/{ticker.ticker}/historical?assetclass=stocks&fromdate={past_90_days}&limit=100&todate={today}"
    data = fetch_data(url_price_hist)
    ticker.price_history = data
    
def get_contract_list(ticker):
    today = datetime.now()
    today_string = today.strftime("%Y-%m-%d")[:10]
    month_from_today = (today + timedelta(60)).strftime("%Y-%m-%d")[:10]
    url_contracts = f"https://api.nasdaq.com/api/quote/{ticker.ticker}/option-chain?assetclass=stocks&limit=100&fromdate={today_string}&todate={month_from_today}&excode=oprac&callput=callput&money=at&type=all"
    data = fetch_data(url_contracts)
    parse_contracts(data, ticker, today)
    print("Fetched: ", ticker.ticker)