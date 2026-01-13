import pandas as pd
from classes.ticker_class import Ticker
from dotenv import load_dotenv
load_dotenv("./.env")
import os

weight_roi = float(os.environ.get("WEIGHT_ROI"))
weight_delta = float(os.environ.get("WEIGHT_DELTA"))
weight_vega = float(os.environ.get("WEIGHT_VEGA"))
weight_iv = float(os.environ.get("WEIGHT_IV"))

def build_trade_old(ticker: Ticker, contract: pd.DataFrame, metrics: dict):
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
        if len(ticker.df_trades):
            tradeIndex = [len(ticker.df_trades)]
        else:
            ticker.df_trades = ticker.df_trades.dropna(axis=1, how='all')
            tradeIndex = [0]
        return pd.DataFrame(trade, index=tradeIndex)

def segment_contracts(ticker: Ticker):
    segments = []
    for date in ticker.unique_dates:
        df_puts = ticker.df_contracts[(ticker.df_contracts["call_put"] == "P") & (ticker.df_contracts["expiry_date"] == date)].copy()
        df_calls = ticker.df_contracts[(ticker.df_contracts["call_put"] == "C") & (ticker.df_contracts["expiry_date"] == date)].copy()
        df_puts = df_puts.sort_values(by="strike", ascending=False).reset_index(drop=True)
        df_calls = df_calls.sort_values(by="strike").reset_index(drop=True)
        segments.append(df_puts)
        segments.append(df_calls)
    return segments


def add_trades(ticker: Ticker):
    #ticker.df_contracts = ticker.df_contracts.sort_values(by=["call_put", "expiry_date", "strike"]).reset_index(drop=True)
    #print(ticker.df_contracts[["stock", "expiry_date", "strike", "call_put", "delta", "bid", "ask"]])

    trades = []
    #Break up into segments of contracts by call/put and expiration
    segments = segment_contracts(ticker)
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
                trade["short_delta"] = float(contract["delta"])
                trade["long_delta"] = float(df.iloc[index+k]["delta"])
                trade["short_vega"] = float(contract["vega"])
                trade["long_vega"] = float(df.iloc[index+k]["vega"])
                trade["short_iv"] = float(contract["imp_vol"])
                trade["long_iv"] = float(df.iloc[index+k]["imp_vol"])
                trade["short_bid"] = float(contract["bid"])
                trade["long_ask"] = float(df.iloc[index+k]["ask"])
                trade["spread"] = 0.0
                trade["max_profit"] = 0.0
                trade["max_loss"] = 0.0
                trade["ROI"] = 0.0
                trade["score"] = 0.0
                if len(ticker.df_trades):
                    tradeIndex = [len(ticker.df_trades)]
                else:
                    ticker.df_trades = ticker.df_trades.dropna(axis=1, how='all')
                    tradeIndex = [0]
                ticker.df_trades = pd.concat([
                    ticker.df_trades, 
                    pd.DataFrame(trade, index=tradeIndex)
                    ], ignore_index=False)
                k += 1

#Calculate spread, max_prof, max_loss, ROI, and score
def calc_trades(ticker: Ticker):
    for index, trade in ticker.df_trades.iterrows():
        spread = abs((trade["short_strike"] - trade["long_strike"]) * 100)
        max_profit = (trade["short_bid"] - trade["long_ask"]) * 100
        max_loss = spread - max_profit
        roi = max_profit / max_loss
        score = roi * weight_roi + (1 - abs(trade["short_delta"])) * weight_delta + trade["short_vega"] * weight_vega + trade["short_iv"] * weight_iv
        ticker.df_trades.loc[index, "spread"] = spread
        ticker.df_trades.loc[index, "max_profit"] = max_profit
        ticker.df_trades.loc[index, "max_loss"] = max_loss
        ticker.df_trades.loc[index, "ROI"] = roi
        ticker.df_trades.loc[index, "score"] = score
        

    # for index, contract in ticker.df_contracts.iterrows():
    #     try:
    #         metrics = {}
    #         metrics["strike_credit"] = float(contract.strike)/1000
    #         metrics["bid_credit"] = float(contract.bid)
    #         metrics["ask_credit"] = float(contract.ask)
    #         k = 1
    #         while(index - k >= 0 and
    #             contract.call_put == "P" and
    #             contract.expiry_date == ticker.df_contracts.iloc[index-k]["expiry_date"] and
    #             contract.call_put == ticker.df_contracts.iloc[index-k]["call_put"]):
    #                 metrics["strike_debit"] = float(ticker.df_contracts.iloc[index-k]["strike"])/1000
    #                 metrics["bid_debit"] = ticker.df_contracts.iloc[index-k]['bid']
    #                 metrics["ask_debit"] = ticker.df_contracts.iloc[index-k]['ask']
    #                 k += 1
    #         while(index + k < len(ticker.df_contracts) and
    #             contract.call_put == "C" and
    #             contract.expiry_date == ticker.df_contracts.iloc[index+k]["expiry_date"] and
    #             contract.call_put == ticker.df_contracts.iloc[index+k]["call_put"]):
    #                 metrics["strike_debit"] = float(ticker.df_contracts.iloc[index+k]["strike"])/1000
    #                 metrics["bid_debit"] = ticker.df_contracts.iloc[index+k]['bid']
    #                 metrics["ask_debit"] = ticker.df_contracts.iloc[index+k]['ask']
    #                 k += 1
    #         build_trade(ticker, contract, metrics)
    #     except: continue
    #     df_trade = build_trade(ticker, contract, metrics)
    #     ticker.df_trades = pd.concat([ticker.df_trades, df_trade], ignore_index=False)

# def trade_filter(ticker):
#     for index, trade in ticker.df_trades.iterrows():
#         ticker.df_trades.loc[index, 'Score'] = (trade.ROI - abs(float(trade.Delta))) / trade.ROI
#     ticker.df_trades = ticker.df_trades.sort_values(by=["Stock", "Score"], ascending=False).reset_index(drop=True)
#     trades_to_drop = []
#     for stock in ticker.df_trades.Stock.unique():
#         stockIndex = ticker.df_trades.Stock.eq(stock).idxmax()
#         for index, trade in ticker.df_trades.iterrows():
#             if trade.Stock == stock and index >= stockIndex + 3:
#                 trades_to_drop.append(index)
#     ticker.df_trades = ticker.df_trades.drop(trades_to_drop).reset_index(drop=True)

def find_trades(ticker: Ticker):
    add_trades(ticker)
    calc_trades(ticker)