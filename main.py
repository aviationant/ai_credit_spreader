import nasdaq_api
import openai_api
import grok_api
import trade_finder
import pandas as pd


tickers = [
    "AAPL",
    "AMGN",
    "AMZN",
    "AXP",
    "BA",
    "CAT",
    "CRM",
    "CSCO",
    "CVX",
    "DIS",
    "GS",
    "HD",
    "HON",
    "IBM",
    "JNJ",
    "JPM",
    "KO",
    "MCD",
    "MMM",
    "MRK",
    "MSFT",
    "NKE",
    "NVDA",
    "PG",
    "SHW",
    "TRV",
    "UNH",
    "V",
    "VZ",
    "WMT"
]

DELTA_MAX = 0.3
DELTA_MIN = 0.1

def main():
    predictions = []

    df_trades = pd.DataFrame(columns=[
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
            "Max Price"]).astype({"Score": "float64"})

    for ticker in tickers:
        df_contracts = pd.DataFrame(columns=[
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
        ])
        df_contracts = nasdaq_api.get_contract_list(ticker, df_contracts)
        price_history = nasdaq_api.get_price_history(ticker)
        unique_dates = df_contracts.expiry_date.unique()

        messages = openai_api.gpt_research(ticker, unique_dates)
        predictions = grok_api.grok_predictor(messages, ticker, unique_dates, price_history)
        print()

        for prediction in predictions:
            df_contracts = nasdaq_api.get_greeks(
                df_contracts, 
                ticker, 
                prediction["date"], 
                prediction["prediction"]
            )

        df_contracts = df_contracts[
            (abs((df_contracts['delta'].astype(float))) >= DELTA_MIN) &
            (abs((df_contracts['delta'].astype(float))) <= DELTA_MAX)
            ].reset_index(drop=True)
        
        df_trades = trade_finder.find_trades(df_contracts, df_trades)
        print()
            
    print()
    print("FINAL: ", df_trades)

if __name__ == "__main__":
    # pass
    main()
