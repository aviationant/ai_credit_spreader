import requests
from datetime import datetime, timedelta
from tqdm import tqdm
import parse_data

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

def get_greeks(df_contracts, ticker, expiry_date, prediction):
    for index, contract in tqdm(df_contracts.iterrows(), total=len(df_contracts), desc=f"Fetching Greeks for {ticker}"):
        if ((prediction >= contract.last_trade) and
            contract.call_put == "P" and
            contract.expiry_date == expiry_date):
            url_greeks = f"https://api.nasdaq.com/api/quote/{ticker}/option-chain?assetclass=stocks&recordID={contract.nasdaq_ticker}"
            data = fetch_data(url_greeks)

        elif ((prediction < contract.last_trade) and
            contract.call_put == "C" and
            contract.expiry_date == expiry_date):
            url_greeks = f"https://api.nasdaq.com/api/quote/{ticker}/option-chain?assetclass=stocks&recordID={contract.nasdaq_ticker}"
            data = fetch_data(url_greeks)
        else:
            continue

        if data:
            greeks_dict, prices_dict = parse_data.parse_greeks_prices(contract, data)
            for col, value in greeks_dict.items():
                df_contracts.at[index, col] = value
            for col, value in prices_dict.items():
                df_contracts.at[index, col] = value

    return df_contracts

def get_price_history(ticker):
    today = datetime.now().strftime("%Y-%m-%d")[:10]
    past_90_days = (datetime.now() - timedelta(90)).strftime("%Y-%m-%d")[:10]
    url_price_hist = f"https://api.nasdaq.com/api/quote/{ticker}/historical?assetclass=stocks&fromdate={past_90_days}&limit=100&todate={today}"
    data = fetch_data(url_price_hist)

    return data
    
def get_contract_list(ticker, df_contracts):
    today = datetime.now().strftime("%Y-%m-%d")[:10]
    month_from_today = (datetime.now() + timedelta(30)).strftime("%Y-%m-%d")[:10]
    url_contracts = f"https://api.nasdaq.com/api/quote/{ticker}/option-chain?assetclass=stocks&limit=100&fromdate={today}&todate={month_from_today}&excode=oprac&callput=callput&money=at&type=all"
    data = fetch_data(url_contracts)
    df_contracts, last_trade = parse_data.parse_contracts(data, ticker, df_contracts)
    print("Fetched: ", ticker)

    return df_contracts, last_trade