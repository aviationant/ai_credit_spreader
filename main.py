from dotenv import load_dotenv
load_dotenv("./.env")
from pymongo.database import Database
from src.trade_finder import find_trades
from src.classes.ticker_class import Ticker
from api.mongo_api import connect_to_db
import pandas as pd
import os

ticker_string = os.environ.get("TICKERS")
tickers = ticker_string.split(",")
predict_bool = os.environ.get("PREDICT")

print(ticker_string)

def main():
    db: Database = connect_to_db()
    companies = []
    i=0
    for ticker in tickers:
        company = Ticker(ticker, db)
        company.get_price_data()
        company.get_unique_dates()
        #if predict_bool == True :
        #    company.get_predictions(db)
        #    company.filter_contracts_by_prediction()
        company.get_ticker_greeks(predict_bool)
        company.filter_contracts_by_greeks()
        find_trades(company)
        companies.append(company)
        i+=1
    all_trades_dfs = [
        company.df_trades.loc[(company.df_trades["max_profit"] > 0) &
                              (company.df_trades["ROI"] > 0.15)]
        .sort_values(by="score")
        .head(3) 
        for company in companies 
        if not company.df_trades.empty
        ]
    if all_trades_dfs:
        df_master_trades = pd.concat(all_trades_dfs, ignore_index=True)
        df_master_trades = df_master_trades.sort_values(by="score", ascending=False).reset_index(drop=True)
        print(df_master_trades.head(20))
    else:
        print("No trade data available from any company.")

if __name__ == "__main__":
    # pass
    main()
