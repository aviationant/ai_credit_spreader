from datetime import datetime
import json
import pandas as pd
import re
import os
from datetime import date

CONTRACT_DAYS_MIN=float(os.environ.get("CONTRACT_DAYS_MIN"))
CONTRACT_DAYS_MAX=float(os.environ.get("CONTRACT_DAYS_MAX"))

def extract_last_trade(ticker, data: json) -> None:
    last_trade_string = data.get('data', {}).get('lastTrade')
    last_trade = re.search("\$(\d+\.?\d*)", last_trade_string)
    ticker.last_trade = float(last_trade.group(1))

def convert_date(date_string) -> list[date, str]:
    date_obj = datetime.strptime(f"{date_string} 2025", "%b %d %Y")
    return date_obj, date_obj.strftime("%y%m%d")

def trade_window(today: date, expiry_date: list[date, str]) -> True:
    days_from_expiry = (expiry_date[0] - today).days
    if days_from_expiry >= CONTRACT_DAYS_MIN and days_from_expiry <= CONTRACT_DAYS_MAX:
        return True
    else: return False

def build_contracts_table(ticker, data: json, today: date) -> pd.DataFrame:
    rows = data.get('data', {}).get('table', {}).get('rows', {})
    contracts = pd.DataFrame()
    for row in rows:
        if not row["expiryDate"]: continue
        expiry_date = convert_date(row["expiryDate"])
        if trade_window(today, expiry_date):
            if row["c_colour"]:
                call_put = "P"
            else:
                call_put = "C"
            contract = {
                "stock": ticker.ticker,
                "expiry_date": expiry_date[1],
                "last_trade": ticker.last_trade,
                "strike": row['strike'],
                "call_put": call_put,
            }
            contract = pd.DataFrame(contract, index=[len(contracts)])
            contracts = pd.concat([contracts, contract], ignore_index=False)
    return contracts

def add_to_df_contracts(ticker, contracts: pd.DataFrame) -> None:
    for index, contract in contracts.iterrows():
        if contract.stock == ticker.ticker:
            ticker.df_contracts.loc[index, "stock"] = contract.stock
            ticker.df_contracts.loc[index, "expiry_date"] = contract.expiry_date
            ticker.df_contracts.loc[index, "last_trade"] = contract.last_trade
            ticker.df_contracts.loc[index, "call_put"] = contract.call_put
            ticker.df_contracts.loc[index, "strike"] = ("000" + contract.strike[:-3] + contract.strike[-2:] + "0")[-8:]
            ticker.df_contracts.loc[index, "ticker"] = contract.stock + contract.expiry_date + contract.call_put + ("000" + contract.strike[:-3] + contract.strike[-2:] + "0")[-8:]
            ticker.df_contracts.loc[index, "nasdaq_ticker"] = (contract.stock.lower() + "-----")[:6] + contract.expiry_date + "c" + ("000" + contract.strike[:-3] + contract.strike[-2:] + "0")[-8:]
            ticker.df_contracts = ticker.df_contracts.fillna(0)
    
def parse_contracts(data: str, ticker, today) -> None:
    data: json = json.loads(data)
    extract_last_trade(ticker, data)
    contracts = build_contracts_table(ticker, data, today)
    add_to_df_contracts(ticker, contracts)

def parse_greeks_prices(contract: pd.DataFrame, data: str) -> list[dict, dict]:
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