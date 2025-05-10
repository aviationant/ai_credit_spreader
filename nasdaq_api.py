import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from time import sleep
from tqdm import tqdm

DELTA_MAX = 0.3
DELTA_MIN = 0.1

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
    date_obj = datetime.strptime(f"{date_string} 2025", "%B %d %Y")
    return [date_obj, date_obj.strftime("%y%m%d")]

def parse_contracts(data, ticker):
    contracts = []
    today = datetime.today()
    data = json.loads(data)
    last_trade = data.get('data', {}).get('lastTrade')[13:19]
    rows = data.get('data', {}).get('table', {}).get('rows', {})
    for row in rows:
        if row['expiryDate'] and (convert_date(row["expiryDate"])[0] - today) > timedelta(6):
            if row["c_colour"]:
                call_put = "P"
            else:
                call_put = "C"
            contract = {
                "underlyingTicker": ticker,
                "expiryDate": row['expiryDate'],
                "last_trade": last_trade,
                "strike": row['strike'],
                "call_put": call_put,
                "ticker": "",
                "nasdaq_ticker": "",
            }
            contracts.append(contract)
    df = pd.DataFrame(contracts)
    for index, contract in df.iterrows():
        contract.expiryDate = convert_date(contract.expiryDate)[1]
        contract.strike = "000" + contract.strike[:-3] + contract.strike[-2:] + "0"
        contract.strike = contract.strike[-8:]
        contract.ticker = contract.underlyingTicker + contract.expiryDate + contract.call_put + contract.strike
        contract.nasdaq_ticker = contract.underlyingTicker.lower() + "--" + contract.expiryDate + "c" + contract.strike

    return df

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
            "impVol": greeks_data["Impvol"]["value"]
    }
    
    prices_dict = {
        "bid": prices_data["Bid"]["value"],
        "ask": prices_data["Ask"]["value"]
    }

    return greeks_dict, prices_dict



def get_greeks(df_contracts, ticker, date, prediction):
    greek_columns = ["delta", "gamma", "rho", "theta", "vega", "impVol"]
    price_columns = ["bid", "ask"]
    for col in greek_columns + price_columns:
        df_contracts[col] = "0"

    for index, contract in tqdm(df_contracts.iterrows(), total=len(df_contracts), desc=f"Fetching Greeks for {ticker}"):
        if ((float(prediction[1:]) >= float(contract["last_trade"])) and
            contract["call_put"] == "P" and
            contract['expiryDate'] == date):

            url_greeks = f"https://api.nasdaq.com/api/quote/{ticker}/option-chain?assetclass=stocks&recordID={contract.nasdaq_ticker}"
            data = fetch_data(url_greeks)

        elif ((float(prediction[1:]) < float(contract["last_trade"])) and
            contract["call_put"] == "C" and
            contract["expiryDate"] == date):
            
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
            
    df_greeks = df_contracts[
        (abs((df_contracts['delta'].astype(float))) >= DELTA_MIN) &
        (abs((df_contracts['delta'].astype(float))) <= DELTA_MAX)
    ].reset_index(drop=True)

    return df_greeks
    

def get_contract_list(ticker):
    url_contracts = f"https://api.nasdaq.com/api/quote/{ticker}/option-chain?assetclass=stocks&limit=100"
    data = fetch_data(url_contracts)
    df_contracts = parse_contracts(data, ticker)
    print("Fetched: ", ticker)

    return df_contracts
