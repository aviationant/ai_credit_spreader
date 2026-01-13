from dotenv import load_dotenv
load_dotenv("./.env")
from pymongo.database import Database
# from trades.trade_finder import find_trades
# from classes.ticker_class import Ticker
from api.mongo_api import connect_to_db
from companies.build_companies_df import build_companies_df
from trades.build_trades_df import build_trades_df
import pandas as pd
import os

companies_string = os.environ.get("COMPANIES")
companies = companies_string.split(",")
predict_bool = os.environ.get("PREDICT")

def main():
    global companies
    print(companies_string)
    companies, df_companies = build_companies_df(companies, predict_bool)
    df_trades = build_trades_df(companies, df_companies)
    exit()


    db: Database = connect_to_db()
    companies = []
    i=0
    for ticker in tickers:
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
