import talib
import numpy as np
import pandas as pd

df = pd.read_csv("./historical_data/NVDA_historical.csv")
close_prices = df["close"].to_numpy()
close_prices = np.flip(close_prices)
dates = df["date"].to_numpy()
dates = np.flip(dates)

macd, signal, hist = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
macd_derivative = np.diff(macd, prepend=np.nan)
macd_derivative_smooth = talib.EMA(macd_derivative, timeperiod=5)
macd_lists = list(zip(dates, macd, macd_derivative_smooth, signal, hist))


df_macd = pd.DataFrame(macd_lists, columns=["date", "macd", "macd_deriv", "signal", "hist"]).reset_index(drop=True)
print(df_macd[df_macd["date"].isin(["05/01/2025",
                                    "05/14/2025",
                                    "06/02/2025",
                                    "06/16/2025",
                                    "07/01/2025",
                                    "07/14/2025",
                                    "08/01/2025",
                                    "08/14/2025",
                                    "09/02/2025",
                                    "09/15/2025"])])