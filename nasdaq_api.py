import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from time import sleep
from tqdm import tqdm
import re

def fetch_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.text
        return data
    else:
        print(f"Request failed with status code: {response.status_code}")

def convert_date(date_string):
    date_obj = datetime.strptime(f"{date_string} 2025", "%b %d %Y")
    return [date_obj, date_obj.strftime("%y%m%d")]

def parse_contracts(data, ticker, df_contracts):
    contracts = []

    today = datetime.today()
    data = json.loads(data)
    last_trade = re.search("\$(\d+\.?\d*)", data.get('data', {}).get('lastTrade'))
    last_trade = last_trade.group(1)
    rows = data.get('data', {}).get('table', {}).get('rows', {})
    for row in rows:
        if row['expiryDate'] and (convert_date(row["expiryDate"])[0] - today) > timedelta(6):
            if row["c_colour"]:
                call_put = "P"
            else:
                call_put = "C"
            contract = {
                "stock": ticker,
                "expiry_date": row['expiryDate'],
                "last_trade": last_trade,
                "strike": row['strike'],
                "call_put": call_put,
                "ticker": "",
                "nasdaq_ticker": "",
                "delta": 0,
                "gamma": 0,
                "rho": 0,
                "theta": 0,
                "vega": 0,
                "imp_vol": 0,
                "bid": 0,
                "ask": 0
            }

            
            contract = pd.DataFrame(contract, index=[len(df_contracts)])
            df_contracts = pd.concat([df_contracts, contract], ignore_index=False)
    
    for index, contract in df_contracts.iterrows():
        if contract.stock == ticker:
            df_contracts.loc[index, "expiry_date"] = convert_date(contract.expiry_date)[1]
            df_contracts.loc[index, "strike"] = ("000" + contract.strike[:-3] + contract.strike[-2:] + "0")[-8:]
            df_contracts.loc[index, "ticker"] = contract.stock + convert_date(contract.expiry_date)[1] + contract.call_put + ("000" + contract.strike[:-3] + contract.strike[-2:] + "0")[-8:]
            df_contracts.loc[index, "nasdaq_ticker"] = (contract.stock.lower() + "-----")[:6] + convert_date(contract.expiry_date)[1] + "c" + ("000" + contract.strike[:-3] + contract.strike[-2:] + "0")[-8:]

    return df_contracts

def parse_greeks_prices(contract, data):
    data = json.loads(data)
    if contract.call_put == "C":
        greeks_data = data.get("data", {}).get("optionChainCallData", {}).get("optionChainGreeksList", {})
        prices_data = data.get("data", {}).get("optionChainCallData", {}).get("optionChainListData", {})
        
    else:
        greeks_data = data.get("data", {}).get("optionChainPutData", {}).get("optionChainGreeksList", {})
        prices_data = data.get("data", {}).get("optionChainPutData", {}).get("optionChainListData", {})

    greeks_dict = {
            "delta": greeks_data["Delta"]["value"],
            "gamma": greeks_data["Gamma"]["value"],
            "rho": greeks_data["Rho"]["value"],
            "theta": greeks_data["Theta"]["value"],
            "vega": greeks_data["Vega"]["value"],
            "imp_vol": greeks_data["Impvol"]["value"]
    }
    
    prices_dict = {
        "bid": prices_data["Bid"]["value"],
        "ask": prices_data["Ask"]["value"]
    }

    return greeks_dict, prices_dict



def get_greeks(df_contracts, ticker, date, prediction):
    for index, contract in tqdm(df_contracts.iterrows(), total=len(df_contracts), desc=f"Fetching Greeks for {ticker}"):
        if ((prediction >= float(contract.last_trade)) and
            contract.call_put == "P" and
            contract.expiry_date == date):

            url_greeks = f"https://api.nasdaq.com/api/quote/{ticker}/option-chain?assetclass=stocks&recordID={contract.nasdaq_ticker}"
            data = fetch_data(url_greeks)

        elif ((prediction < float(contract.last_trade)) and
            contract.call_put == "C" and
            contract.expiry_date == date):
            
            url_greeks = f"https://api.nasdaq.com/api/quote/{ticker}/option-chain?assetclass=stocks&recordID={contract.nasdaq_ticker}"
            data = fetch_data(url_greeks)
        else:
            continue

        if data:
            greeks_dict, prices_dict = parse_greeks_prices(contract, data)

            for col, value in greeks_dict.items():
                df_contracts.at[index, col] = value
            for col, value in prices_dict.items():
                df_contracts.at[index, col] = value

    return df_contracts

def get_price_history(ticker):
    today = datetime.now().strftime("%Y-%m-%d")[:10]
    past_90 = (datetime.now() - timedelta(90)).strftime("%Y-%m-%d")[:10]
    url_price_hist = f"https://api.nasdaq.com/api/quote/{ticker}/historical?assetclass=stocks&fromdate={past_90}&limit=100&todate={today}"
    data = fetch_data(url_price_hist)

    return data
    

def get_contract_list(ticker, df_contracts):
    today = datetime.now().strftime("%Y-%m-%d")[:10]
    one_month = (datetime.now() + timedelta(30)).strftime("%Y-%m-%d")[:10]
    url_contracts = f"https://api.nasdaq.com/api/quote/{ticker}/option-chain?assetclass=stocks&limit=100&fromdate={today}&todate={one_month}&excode=oprac&callput=callput&money=at&type=all"
    data = fetch_data(url_contracts)
    df_contracts = parse_contracts(data, ticker, df_contracts)
    print("Fetched: ", ticker)

    return df_contracts