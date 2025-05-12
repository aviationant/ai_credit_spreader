import nasdaq_api
import openai_api
import grok_api
import trade_finder
import pandas as pd


tickers = [
    "AAPL",
    "MSFT",
    "NVDA",
    # "AXP",
    # "CAT"

]

def main():
    tables = []
    predictions = []

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

    for ticker in tickers:
        df_contracts = nasdaq_api.get_contract_list(ticker, df_contracts)
        price_history = nasdaq_api.get_price_history(ticker)
        unique_dates = df_contracts['expiry_date'].unique()

        messages = openai_api.gpt_research(ticker, unique_dates)
        predictions = grok_api.grok_predictor(messages, ticker, unique_dates, price_history)
        print()

        for prediction in predictions:
            #Fix .get_greeks to .loc existing df_contracts values instead of concat greeks
            df_greeks = nasdaq_api.get_greeks(
                df_contracts, 
                ticker, 
                prediction["date"], 
                prediction["prediction"]
            )
            tables.append(df_greeks)


        print()
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
            "Score"]).astype({"Score": "float64"})
        
        for table in tables:
            df_trades = trade_finder.find_trades(table, df_trades)
            
    print()
    print(df_trades)

    # print()
    # print(tables)
    

if __name__ == "__main__":
    # pass
    main()
