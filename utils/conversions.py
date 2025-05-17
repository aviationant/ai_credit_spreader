import pandas as pd

def convert_float(value: str):
    try:
        return float(value)
    except ValueError:
        return "Invalid input: cannot convert to float"
    
def clean_prices(response: str) -> list[float]:
    prices = response.split(",")
    for price in prices:
        price = convert_float(price)
    return prices

def convert_df_to_float(df):
    numeric_cols = ["current_price", "prediction", "last_trade", "delta", "gamma", "rho", "theta", "vega", "imp_vol", "bid", "ask"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")