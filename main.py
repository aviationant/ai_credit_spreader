import nasdaq_api
import openai_api
import trade_finder
import pandas as pd


tickers = [
    "AAPL",
    "MSFT",
    # "NVDA"
]

def main():
    tables = []
    predictions = []

    for ticker in tickers:
        df_contracts = nasdaq_api.get_contract_list(ticker)
        unique_dates = df_contracts['expiryDate'].unique()

        predictions = openai_api.gpt_predictor(ticker, unique_dates)
        print()

        for prediction in predictions:
            df_greeks = nasdaq_api.get_greeks(
                df_contracts, 
                ticker, 
                prediction["date"], 
                prediction["prediction"]
            )
            tables.append(df_greeks)

        print()
        df_trades = pd.DataFrame(columns=["Stock", "Ticker", "Call/Put", "Strike Cred.", "Strike Deb.", "Mid Credit", "Mid Debit", "Max Prof", "Max Loss", "ROI"])
        for table in tables:
            df_trades = trade_finder.find_trades(table, df_trades)
            
        print()
        print(df_trades)

    # print()
    # print(tables)
    

if __name__ == "__main__":
    # pass
    main()
