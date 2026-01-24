import pandas as pd
# from classes.ticker_class import Ticker
from dotenv import load_dotenv
load_dotenv("./.env")
import os

weight_roi = float(os.environ.get("WEIGHT_ROI"))
weight_delta = float(os.environ.get("WEIGHT_DELTA"))
weight_vega = float(os.environ.get("WEIGHT_VEGA"))
weight_iv = float(os.environ.get("WEIGHT_IV"))

def build_trade_old(company, contract: pd.DataFrame, metrics: dict):
    mid_price_credit = (metrics["bid_credit"] + metrics["ask_credit"]) / 2
    mid_price_debit = (metrics["bid_debit"] + metrics["ask_debit"]) / 2
    if contract.call_put == "P":
        max_profit = float((metrics["bid_credit"] - metrics["ask_debit"]) * 100)
        spread = float((metrics["strike_credit"] - metrics["strike_debit"]) * 100)
    else:
        max_profit = float((metrics["bid_debit"] - metrics["ask_credit"]) * 100)
        spread = float((metrics["strike_debit"] - metrics["strike_credit"]) * 100)
    max_loss = spread - max_profit
    roi = (max_profit / max_loss)
    #Probability of success
    min_price = abs(float(contract.delta)) * (metrics["strike_credit"] - metrics["strike_debit"])
    if abs(max_profit / spread) > abs(float(contract.delta)) * 0.0001:
        trade = {
            "Stock": contract.stock,
            "Ticker": contract.ticker,
            "Call/Put": contract.call_put,
            "Strike Cred.": metrics["strike_credit"],
            "Strike Deb.": metrics["strike_debit"],
            "Bid Credit": metrics["bid_credit"],
            "Ask Debit": metrics["ask_debit"],
            "Max Prof": max_profit,
            "Max Loss": max_loss,
            "ROI": roi,
            "Delta": contract.delta,
            "Score": 0.0,
            "Min Price": min_price
        }
        if len(company.df_trades):
            tradeIndex = [len(company.df_trades)]
        else:
            company.df_trades = company.df_trades.dropna(axis=1, how='all')
            tradeIndex = [0]
        return pd.DataFrame(trade, index=tradeIndex)

def segment_contracts(company):
    segments = []
    for date in company.expiry_dates:
        df_puts = company.df_contracts[(company.df_contracts["call_put"] == "P") & (company.df_contracts["expiry_date"] == date)].copy()
        df_calls = company.df_contracts[(company.df_contracts["call_put"] == "C") & (company.df_contracts["expiry_date"] == date)].copy()
        df_puts = df_puts.sort_values(by="strike", ascending=False).reset_index(drop=True)
        df_calls = df_calls.sort_values(by="strike").reset_index(drop=True)
        segments.append(df_puts)
        segments.append(df_calls)
    return segments


def add_trades(company):
    #company.df_contracts = company.df_contracts.sort_values(by=["call_put", "expiry_date", "strike"]).reset_index(drop=True)
    #print(company.df_contracts[["stock", "expiry_date", "strike", "call_put", "delta", "bid", "ask"]])

    trades = []
    #Break up into segments of contracts by call/put and expiration
    segments = segment_contracts(company)
    for df in segments:
        for index, contract in df.iterrows():
            if index >= len(df)-1: continue
            k = 1
            while k < len(df)-index:
                trade = {}
                trade["stock"] = contract["stock"]
                trade["call_put"] = contract["call_put"]
                trade["expiry_date"] = contract["expiry_date"]
                trade["short_strike"] = float(contract["strike"]) / 1000
                trade["long_strike"] = float(df.iloc[index+k]["strike"]) / 1000
                trade["short_delta"] = round(float(contract["delta"]), 3)
                trade["long_delta"] = round(float(df.iloc[index+k]["delta"]), 3)
                trade["short_vega"] = round(float(contract["vega"]), 3)
                trade["long_vega"] = round(float(df.iloc[index+k]["vega"]), 3)
                trade["short_iv"] = round(float(contract["imp_vol"]), 3)
                trade["long_iv"] = round(float(df.iloc[index+k]["imp_vol"]), 3)
                trade["short_bid"] = float(contract["bid"])
                trade["short_ask"] = float(contract["ask"])
                trade["long_bid"] = float(df.iloc[index+k]["bid"])
                trade["long_ask"] = float(df.iloc[index+k]["ask"])
                trade["spread"] = 0.0
                trade["max_profit"] = 0.0
                trade["max_loss"] = 0.0
                trade["ROI"] = 0.0
                trade["score"] = 0.0
                if len(company.df_trades):
                    tradeIndex = [len(company.df_trades)]
                else:
                    company.df_trades = company.df_trades.dropna(axis=1, how='all')
                    tradeIndex = [0]
                company.df_trades = pd.concat([
                    company.df_trades, 
                    pd.DataFrame(trade, index=tradeIndex)
                    ], ignore_index=False)
                k += 1

#Calculate spread, max_prof, max_loss, ROI, and score
def calc_trades(company):
    for index, trade in company.df_trades.iterrows():
        short_mid = (trade["short_bid"] + trade["short_ask"]) / 2
        long_mid = (trade["long_bid"] + trade["long_ask"]) / 2
        spread = abs((trade["short_strike"] - trade["long_strike"]) * 100)
        max_profit = (short_mid - long_mid) * 100
        max_loss = spread - max_profit
        roi = max_profit / max_loss
        score = roi * weight_roi + (1 - abs(trade["short_delta"])) * weight_delta + trade["short_vega"] * weight_vega + trade["short_iv"] * weight_iv
        company.df_trades.loc[index, "spread"] = spread
        company.df_trades.loc[index, "max_profit"] = max_profit
        company.df_trades.loc[index, "max_loss"] = max_loss
        company.df_trades.loc[index, "ROI"] = round(roi, 3)
        company.df_trades.loc[index, "score"] = round(score, 3)
        

    # for index, contract in company.df_contracts.iterrows():
    #     try:
    #         metrics = {}
    #         metrics["strike_credit"] = float(contract.strike)/1000
    #         metrics["bid_credit"] = float(contract.bid)
    #         metrics["ask_credit"] = float(contract.ask)
    #         k = 1
    #         while(index - k >= 0 and
    #             contract.call_put == "P" and
    #             contract.expiry_date == company.df_contracts.iloc[index-k]["expiry_date"] and
    #             contract.call_put == company.df_contracts.iloc[index-k]["call_put"]):
    #                 metrics["strike_debit"] = float(company.df_contracts.iloc[index-k]["strike"])/1000
    #                 metrics["bid_debit"] = company.df_contracts.iloc[index-k]['bid']
    #                 metrics["ask_debit"] = company.df_contracts.iloc[index-k]['ask']
    #                 k += 1
    #         while(index + k < len(company.df_contracts) and
    #             contract.call_put == "C" and
    #             contract.expiry_date == company.df_contracts.iloc[index+k]["expiry_date"] and
    #             contract.call_put == company.df_contracts.iloc[index+k]["call_put"]):
    #                 metrics["strike_debit"] = float(company.df_contracts.iloc[index+k]["strike"])/1000
    #                 metrics["bid_debit"] = company.df_contracts.iloc[index+k]['bid']
    #                 metrics["ask_debit"] = company.df_contracts.iloc[index+k]['ask']
    #                 k += 1
    #         build_trade(ticker, contract, metrics)
    #     except: continue
    #     df_trade = build_trade(ticker, contract, metrics)
    #     company.df_trades = pd.concat([company.df_trades, df_trade], ignore_index=False)

# def trade_filter(company):
#     for index, trade in company.df_trades.iterrows():
#         company.df_trades.loc[index, 'Score'] = (trade.ROI - abs(float(trade.Delta))) / trade.ROI
#     company.df_trades = company.df_trades.sort_values(by=["Stock", "Score"], ascending=False).reset_index(drop=True)
#     trades_to_drop = []
#     for stock in company.df_trades.Stock.unique():
#         stockIndex = company.df_trades.Stock.eq(stock).idxmax()
#         for index, trade in company.df_trades.iterrows():
#             if trade.Stock == stock and index >= stockIndex + 3:
#                 trades_to_drop.append(index)
#     company.df_trades = company.df_trades.drop(trades_to_drop).reset_index(drop=True)

def find_trades(company):
    add_trades(company)
    calc_trades(company)