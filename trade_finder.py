import pandas as pd

def find_trades_long(df_all, df_trades):
    for index, row in df_all.iterrows():
        if row["call_put"] != "P":
            continue

        strike_credit = float(row['strike'])/1000
        bid_credit = float(row['bid'])
        ask_credit = float(row['ask'])
        mid_price_credit = (bid_credit + ask_credit) / 2
        k = 1
        while(index - k >= 0 and
            row["expiryDate"] == df_all.iloc[index-k]["expiryDate"] and
            row["call_put"] == df_all.iloc[index-k]["call_put"] and
            row['call_put'] == "P"):

            strike_debit = float(df_all.iloc[index-k]["strike"])/1000
            bid_debit = float(df_all.iloc[index-k]['bid'])
            ask_debit = float(df_all.iloc[index-k]['ask'])
            mid_price_debit = (bid_debit + ask_debit) / 2
            max_profit = (mid_price_credit - mid_price_debit) * 100
            max_loss = (strike_credit - strike_debit) * 100 - max_profit
            roi = (max_profit / max_loss)
            
            if roi > abs(float(row["delta"])):
                trade = {
                    "Stock": row["underlyingTicker"],
                    "Ticker": row["ticker"],
                    "Call/Put": row["call_put"],
                    "Strike Cred.": strike_credit,
                    "Strike Deb.": strike_debit,
                    "Mid Credit": mid_price_credit,
                    "Mid Debit": mid_price_debit,
                    "Max Prof": max_profit,
                    "Max Loss": max_loss,
                    "ROI": roi
                }

                if len(df_trades):
                    tradeIndex = [len(df_trades)]
                else:
                    df_trades = df_trades.dropna(axis=1, how='all')
                    tradeIndex = [0]

                df_trade = pd.DataFrame(trade, index=tradeIndex)
                df_trades = pd.concat([df_trades, df_trade], ignore_index=False)
                
            k += 1
            continue
    return df_trades

def find_trades_short(df_all, df_trades):
    for index, row in df_all.iterrows():
        if row["call_put"] != "C":
            continue
        
        strike_credit = float(row['strike'])/1000
        bid_credit = float(row['bid'])
        ask_credit = float(row['ask'])
        mid_price_credit = (bid_credit + ask_credit) / 2
        k = 1
        while(index + k < len(df_all) and
            row["expiryDate"] == df_all.iloc[index+k]["expiryDate"] and
            row["call_put"] == df_all.iloc[index+k]["call_put"] and
            row['call_put'] == "C"):

            strike_debit = float(df_all.iloc[index+k]["strike"])/1000
            bid_debit = float(df_all.iloc[index+k]['bid'])
            ask_debit = float(df_all.iloc[index+k]['ask'])
            mid_price_debit = (bid_debit + ask_debit) / 2
            max_profit = (mid_price_credit - mid_price_debit) * 100
            max_loss = (strike_debit - strike_credit) * 100 - max_profit
            roi = (max_profit / max_loss)
            
            if roi > abs(float(row["delta"])):
                trade = {
                    "Stock": row["underlyingTicker"],
                    "Ticker": row["ticker"],
                    "Call/Put": row["call_put"],
                    "Strike Cred.": strike_credit,
                    "Strike Deb.": strike_debit,
                    "Mid Credit": mid_price_credit,
                    "Mid Debit": mid_price_debit,
                    "Max Prof": max_profit,
                    "Max Loss": max_loss,
                    "ROI": roi
                }
                
                if len(df_trades):
                    tradeIndex = [len(df_trades)]
                else:
                    df_trades = df_trades.dropna(axis=1, how='all')
                    tradeIndex = [0]

                df_trade = pd.DataFrame(trade, index=tradeIndex)
                df_trades = pd.concat([df_trades, df_trade], ignore_index=False)

            k += 1
            continue
    return df_trades

def find_trades(df_all, df_trades):
    df_trades = find_trades_long(df_all, df_trades)
    df_trades = find_trades_short(df_all, df_trades)

    return df_trades