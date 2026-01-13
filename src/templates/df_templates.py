import pandas as pd

def get_df_template(df_type):
    if df_type == "trades":
        return pd.DataFrame(
            columns=[
                "Stock",
                "Call/Put",
                "Expiry",
                "Short Strike",
                "Long Strike",
                "Short Delta",
                "Long Delta",
                "Short Vega",
                "Long Vega",
                "Short IV",
                "Long IV",
                "Short Bid",
                "Long Ask",
                "Spread",
                "Max Profit",
                "Max Loss",
                "ROI",
                "Score"
            ]).astype({
                "Stock": "string",
                "Call/Put": "string",
                "Expiry": "string",
                "Short Strike": "float64",
                "Long Strike": "float64",
                "Short Delta": "float64",
                "Long Delta": "float64",
                "Short Vega": "float64",
                "Long Vega": "float64",
                "Short IV": "float64",
                "Long IV": "float64",
                "Short Bid": "float64",
                "Long Ask": "float64",
                "Spread": "float64",
                "Max Profit": "float64",
                "Max Loss": "float64",
                "ROI": "float64",
                "Score": "float64"
            })
    
    elif df_type == "contracts":
        return pd.DataFrame(
            columns=[
                "stock",
                "expiry_date",
                "last_trade",
                "strike",
                "call_put",
                "ticker",
                "nasdaq_ticker",
                "delta",
                "gamma",
                "rho",
                "theta",
                "vega",
                "imp_vol",
                "bid",
                "ask"
            ]).astype({
                "stock": "string",
                "expiry_date": "string",
                "last_trade": "float64",
                "strike": "string",
                "call_put": "string",
                "ticker": "string",
                "nasdaq_ticker": "string",
                "delta": "float64",
                "gamma": "float64",
                "rho": "float64",
                "theta": "float64",
                "vega": "float64",
                "imp_vol": "float64",
                "bid": "float64",
                "ask": "float64"
            })
    elif df_type == "predictions":
        return pd.DataFrame(
            columns=[
                "date",
                "current_price",
                "ticker",
                "expiry_date",
                "prediction"
            ]).astype({
                "date": "string",
                "current_price": "float64",
                "ticker": "string",
                "expiry_date": "string",
                "prediction": "float64"
            })
    elif df_type == "companies":
        return pd.DataFrame(
            columns=[
                "company",
                "last_trade",
                "direction",
                "expiry_dates",
                "earnings_date",
                "SMA_fast_slope",
                "SMA_slow_slope",
                "dir_streak"
            ]).astype({
                "company": "string",
                "last_trade": "float64",
                "direction": "string",
                "earnings_date": "string",
                "SMA_fast_slope": "float64",
                "SMA_slow_slope": "float64",
                "dir_streak": "int"
            })
    elif df_type == "price_history":
        return pd.DataFrame(
            columns=[
                "date",
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]).astype({
                "date": "string",
                "open": "float64",
                "high": "float64",
                "low": "float64",
                "close": "float64",
                "volume": "float64"
            })