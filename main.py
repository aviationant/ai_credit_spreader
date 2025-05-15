import hooks.nasdaq_api as nasdaq_api
import apis.openai_api as openai_api
import apis.grok_api as grok_api
import trade_finder
from df_templates import get_df_template
import pandas as pd
from datetime import date
import hooks.mongo_hook as mongo_hook

tickers = [
    # "AAPL",
    # "AMGN",
    "AMZN",
    # "AXP",
    # "BA",
    # "CAT",
    # "CRM",
    # "CSCO",
    # "CVX",
    # "DIS",
    # "GS",
    # "HD",
    # "HON",
    # "IBM",
    # "JNJ",
    # "JPM",
    # "KO",
    # "MCD",
    # "MMM",
    # "MRK",
    # "MSFT",
    # "NKE",
    # "NVDA",
    # "PG",
    # "SHW",
    # "TRV",
    # "UNH",
    # "V",
    # "VZ",
    "WMT"
]

DELTA_MAX = 0.3
DELTA_MIN = 0.1

def main():
    today = date.today()
    today = today.strftime("%Y-%m-%d")
    predictions = []
    df_trades = get_df_template("trades")

    db = mongo_hook.connect_to_db()

    for ticker in tickers:
        df_contracts = get_df_template("contracts")
        df_contracts, last_trade = nasdaq_api.get_contract_list(ticker, df_contracts)
        price_history = nasdaq_api.get_price_history(ticker)
        unique_dates = df_contracts.expiry_date.unique()

        try:
            predictions = mongo_hook.get_db_predictions(db)
            df_predictions = pd.DataFrame(predictions)
        except:
            print("Failed to get DB.")

        if df_predictions.empty:
            df_predictions = get_df_template("predictions")

        if today in df_predictions["date"].values and ticker in df_predictions["ticker"].values:
            predictions = [row for index, row in df_predictions.iterrows() if row["ticker"] == ticker]
        else:
            messages = openai_api.gpt_research(ticker, unique_dates)
            predictions = grok_api.grok_predictor(
                messages,
                ticker,
                unique_dates,
                price_history,
                last_trade)
            df_predictions = pd.concat([df_predictions, pd.DataFrame(predictions)])
            if "_id" in df_predictions:
                df_predictions = df_predictions[df_predictions["_id"].isna()].drop("_id", axis=1)

            mongo_hook.add_db_items(db, df_predictions.to_dict('records'))
        
        print()

        for prediction in predictions:
            df_contracts = nasdaq_api.get_greeks(
                df_contracts, 
                ticker, 
                prediction["expiry_date"], 
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
