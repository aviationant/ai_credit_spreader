from datetime import datetime, timedelta
import json
import pandas as pd
import re

def convert_date(date_string):
    date_obj = datetime.strptime(f"{date_string} 2025", "%b %d %Y")
    return [date_obj, date_obj.strftime("%y%m%d")]

def parse_contracts(data, ticker, df_contracts):
    today = datetime.today()
    data = json.loads(data)
    last_trade = re.search("\$(\d+\.?\d*)", data.get('data', {}).get('lastTrade'))
    last_trade = float(last_trade.group(1))
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

    return df_contracts, last_trade

def parse_greeks_prices(contract, data):
    data = json.loads(data)
    if contract.call_put == "C":
        greeks_data = data.get("data", {}).get("optionChainCallData", {}).get("optionChainGreeksList", {})
        prices_data = data.get("data", {}).get("optionChainCallData", {}).get("optionChainListData", {})
        
    else:
        greeks_data = data.get("data", {}).get("optionChainPutData", {}).get("optionChainGreeksList", {})
        prices_data = data.get("data", {}).get("optionChainPutData", {}).get("optionChainListData", {})

    greeks_dict = {
            "delta": float(greeks_data["Delta"]["value"]),
            "gamma": float(greeks_data["Gamma"]["value"]),
            "rho": float(greeks_data["Rho"]["value"]),
            "theta": float(greeks_data["Theta"]["value"]),
            "vega": float(greeks_data["Vega"]["value"]),
            "imp_vol": float(greeks_data["Impvol"]["value"])
    }
    
    prices_dict = {
        "bid": float(prices_data["Bid"]["value"]),
        "ask": float(prices_data["Ask"]["value"])
    }

    return greeks_dict, prices_dict