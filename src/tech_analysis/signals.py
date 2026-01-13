def calc_sma(df_prices, period):
    df_prices['SMA_5'] = df_prices['Close'].rolling(window=5).mean()

def calc_sma_slope(df_prices, period):
    today_sma = df_prices["close"].iloc[:int(period)].mean()
    yester_sma = df_prices["close"].iloc[1:int(period)+1].mean()
    return today_sma / yester_sma

def calc_streak(df_prices):
    streak = 1
    if df_prices["close"].iloc[0] >= df_prices["close"].iloc[11]:
        direction = "bull"
    else: direction = "bear"
    for index, row in df_prices.iterrows():
        if ((row["close"] >= df_prices["close"].iloc[index+11] and
            direction == "bull") or
        (row["close"] <= df_prices["close"].iloc[index+11] and
            direction == "bear")):
            streak += 1
        else: break
    return [direction, streak]