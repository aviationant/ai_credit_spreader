import pandas as pd

def get_df_template(df_type):
    if df_type == "trades":
        return pd.DataFrame(columns=[
            "Stock",
            "Ticker",
            "Call/Put",
            "Strike Cred.",
            "Strike Deb.",
            "Mid Credit",
            "Mid Debit",
            "Max Prof",
            "Max Loss",
            "ROI",
            "Score",
            "Max Price"
        ]).astype({
            "Stock": "string",
            "Ticker": "string",
            "Call/Put": "string",
            "Strike Cred.": "float64",
            "Strike Deb.": "float64",
            "Mid Credit": "float64",
            "Mid Debit": "float64",
            "Max Prof": "float64",
            "Max Loss": "float64",
            "ROI": "float64",
            "Score": "float64",
            "Max Price": "float64"
        })
    
    elif df_type == "contracts":
        return pd.DataFrame(columns=[
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
        return pd.DataFrame(columns=[
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