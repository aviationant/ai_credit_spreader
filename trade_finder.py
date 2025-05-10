def find_trades_long(df_all):
    for index, row in df_all.iterrows():
        if row["call_put"] != "P":
            continue

        strike_credit = float(row['strike'])/1000
        bid_credit = float(row['bid'])
        ask_credit = float(row['ask'])
        avg_price_credit = (bid_credit + ask_credit) / 2
        k = 1
        while(index - k >= 0 and
            row["expiryDate"] == df_all.iloc[index-k]["expiryDate"] and
            row["call_put"] == df_all.iloc[index-k]["call_put"] and
            row['call_put'] == "P"):

            strike_debit = float(df_all.iloc[index-k]["strike"])/1000
            bid_debit = float(df_all.iloc[index-k]['bid'])
            ask_debit = float(df_all.iloc[index-k]['ask'])
            avg_price_debit = (bid_debit + ask_debit) / 2
            max_profit = (avg_price_credit - avg_price_debit) * 100
            max_loss = (strike_credit - strike_debit) * 100 - max_profit
            roi = (max_profit / max_loss)
            
            if roi > abs(float(row["delta"])):
                print("Ticker: ", row["underlyingTicker"])
                print("Expiry: ", row["expiryDate"])
                print("Strike Credit: ", strike_credit)
                print("Strike Debit: ", strike_debit)
                print("Avg Credit: ", avg_price_credit)
                print("Avg Debit: ", avg_price_debit)
                print("Max Prof: ", max_profit)
                print("Max Loss: ", max_loss)
                print("ROI: ", roi * 100, "%")
                print()
            k += 1
            continue

def find_trades_short(df_all):
    for index, row in df_all.iterrows():
        if row["call_put"] != "C":
            continue
        
        strike_credit = float(row['strike'])/1000
        bid_credit = float(row['bid'])
        ask_credit = float(row['ask'])
        avg_price_credit = (bid_credit + ask_credit) / 2
        k = 1
        while(index + k < len(df_all) and
            row["expiryDate"] == df_all.iloc[index+k]["expiryDate"] and
            row["call_put"] == df_all.iloc[index+k]["call_put"] and
            row['call_put'] == "C"):

            strike_debit = float(df_all.iloc[index+k]["strike"])/1000
            bid_debit = float(df_all.iloc[index+k]['bid'])
            ask_debit = float(df_all.iloc[index+k]['ask'])
            avg_price_debit = (bid_debit + ask_debit) / 2
            max_profit = (avg_price_credit - avg_price_debit) * 100
            max_loss = (strike_debit - strike_credit) * 100 - max_profit
            roi = (max_profit / max_loss)
            
            if roi > abs(float(row["delta"])):
                print("Ticker: ", row["underlyingTicker"])
                print("Expiry: ", row["expiryDate"])
                print("Strike Credit: ", strike_credit)
                print("Strike Debit: ", strike_debit)
                print("Avg Credit: ", avg_price_credit)
                print("Avg Debit: ", avg_price_debit)
                print("Max Prof: ", max_profit)
                print("Max Loss: ", max_loss)
                print("ROI: ", roi * 100, "%")
                print()
            k += 1
            continue

def find_trades(df_all):
    find_trades_long(df_all)
    find_trades_short(df_all)