import torch
import yfinance as yf
import pandas as pd
import pandas_ta as ta  # For technical indicators
from chronos import ChronosPipeline

# Fetch historical data (e.g., AAPL)
data = yf.download('AAPL', start='2020-01-01', end='2025-09-01')
df = data[['Open', 'High', 'Low', 'Close', 'Volume']]

# Compute technical indicators (example: add SMA, RSI, MACD)
df['SMA_20'] = ta.sma(df['Close'], length=20)
df['RSI_14'] = ta.rsi(df['Close'], length=14)
macd = ta.macd(df['Close'])
df = pd.concat([df, macd], axis=1)

print(ta.macd(df['Close']))

# Use closing price + indicators as multivariate series (drop NaNs)
series = df[['Close', 'SMA_20', 'RSI_14', 'MACD', 'MACD_Hist', 'MACD_Signal']].dropna().values  # Shape: (time_steps, channels)

# Load model (use small for GTX 1070)
pipeline = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-small",
    device_map="cuda",
    torch_dtype=torch.bfloat16,
)

# Prepare context (historical data as tensor)
context = torch.tensor(series)

# Predict 60 days ahead
prediction_length = 60
forecast = pipeline.predict(context, prediction_length)  # Returns samples for probabilistic forecast

# Extract median and intervals
low, median, high = torch.quantile(forecast[0], torch.tensor([0.1, 0.5, 0.9]), dim=0).numpy()

# median[0] is the forecast for the first channel (Close), etc.
print("Median forecast:", median[:, 0])  # Focus on closing price channel