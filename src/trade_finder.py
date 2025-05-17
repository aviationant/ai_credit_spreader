import pandas as pd
from src.classes.ticker_class import Ticker

def build_trade(ticker: Ticker, contract: pd.DataFrame, metrics: dict):
    mid_price_credit = (metrics["bid_credit"] + metrics["ask_credit"]) / 2
    mid_price_debit = (metrics["bid_debit"] + metrics["ask_debit"]) / 2
    max_profit = (mid_price_credit - mid_price_debit) * 100
    max_loss = (metrics["strike_credit"] - metrics["strike_debit"]) * 100 - max_profit
    roi = (max_profit / max_loss)
    min_price = abs(float(contract.delta)) * (metrics["strike_credit"] - metrics["strike_debit"])
    if roi > abs(float(contract.delta)):
        trade = {
            "Stock": contract.stock,
            "Ticker": contract.ticker,
            "Call/Put": contract.call_put,
            "Strike Cred.": metrics["strike_credit"],
            "Strike Deb.": metrics["strike_debit"],
            "Bid Credit": mid_price_credit,
            "Ask Debit": mid_price_debit,
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

def add_trades(ticker: Ticker):
    for index, contract in ticker.df_contracts.iterrows():
        try:
            metrics = {}
            metrics["strike_credit"] = float(contract.strike)/1000
            metrics["bid_credit"] = float(contract.bid)
            metrics["ask_credit"] = float(contract.ask)
            k = 1
            while(index - k >= 0 and
                contract.expiry_date == ticker.df_contracts.iloc[index-k]["expiry_date"] and
                contract.call_put == ticker.df_contracts.iloc[index-k]["call_put"] and
                contract.call_put == "P"):
                    metrics["strike_debit"] = float(ticker.df_contracts.iloc[index-k]["strike"])/1000
                    metrics["bid_debit"] = ticker.df_contracts.iloc[index-k]['bid']
                    metrics["ask_debit"] = ticker.df_contracts.iloc[index-k]['ask']
                    k += 1
            while(index + k < len(ticker.df_contracts) and
                contract.expiry_date == ticker.df_contracts.iloc[index+k]["expiry_date"] and
                contract.call_put == ticker.df_contracts.iloc[index+k]["call_put"] and
                contract.call_put == "C"):
                    metrics["strike_debit"] = float(ticker.df_contracts.iloc[index+k]["strike"])/1000
                    metrics["bid_debit"] = ticker.df_contracts.iloc[index+k]['bid']
                    metrics["ask_debit"] = ticker.df_contracts.iloc[index+k]['ask']
                    k += 1
            build_trade(ticker, contract, metrics)
        except: continue
        df_trade = build_trade(ticker, contract, metrics)
        ticker.df_trades = pd.concat([ticker.df_trades, df_trade], ignore_index=False)

def trade_filter(ticker):
    for index, trade in ticker.df_trades.iterrows():
        ticker.df_trades.loc[index, 'Score'] = (trade.ROI - abs(float(trade.Delta))) / trade.ROI
    ticker.df_trades = ticker.df_trades.sort_values(by=["Stock", "Score"], ascending=False).reset_index(drop=True)
    trades_to_drop = []
    for stock in ticker.df_trades.Stock.unique():
        stockIndex = ticker.df_trades.Stock.eq(stock).idxmax()
        for index, trade in ticker.df_trades.iterrows():
            if trade.Stock == stock and index >= stockIndex + 3:
                trades_to_drop.append(index)
    ticker.df_trades = ticker.df_trades.drop(trades_to_drop).reset_index(drop=True)

def find_trades(ticker: Ticker):
    add_trades(ticker)
    trade_filter(ticker)
    ticker.df_trades = ticker.df_trades.sort_values(by=["Score"], ascending=False).reset_index(drop=True)