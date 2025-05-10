import nasdaq_api
import openai_api
import trade_finder


tickers = [
    "AAPL",
    "MSFT",
    "NVDA"
]

def main():
    tables = []
    predictions = []

    for ticker in tickers:
        df_contracts = nasdaq_api.get_contract_list(ticker)
        unique_dates = df_contracts['expiryDate'].unique()

        for date in unique_dates:
            gpt_prediction = openai_api.gpt_predictor(ticker, date)
            predictions.append({
                "ticker": ticker,
                "date": date,
                "prediction": gpt_prediction
            })
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
        for table in tables:
            trade_finder.find_trades(table)

    print()
    print(tables)
    

if __name__ == "__main__":
    main()
