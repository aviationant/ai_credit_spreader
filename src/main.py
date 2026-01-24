import os

import pandas as pd

# from trades.trade_finder import find_trades
# from classes.ticker_class import Ticker
from api.mongo_api import connect_to_db
from companies.build_companies_df import build_companies_df
from dotenv import load_dotenv
from pymongo.database import Database
from trades.build_trades_df import build_trades_df

load_dotenv("./.env")

companies_string = os.environ.get("COMPANIES")
predict_bool = os.environ.get("PREDICT")
max_spread = float(os.environ.get("MAX_SPREAD"))


def main():
    companies = companies_string.split(",")
    print(f"Analyzing {len(companies)} tickers")
    print(companies_string)
    companies, df_companies = build_companies_df(companies, predict_bool)
    print(
        df_companies[
            (df_companies["direction"] != "none")
            & (df_companies["expiry_dates"].str.len() > 0)
            & (df_companies["dir_streak"] >= 12)
            & (df_companies["dir_streak"] <= 33)
        ]
        .head(40)
        .reset_index(drop=True)
    )
    df_trades = build_trades_df(companies, df_companies)
    all_trades_dfs = [
        company.df_trades.loc[
            (company.df_trades["max_profit"] > 0)
            & (company.df_trades["ROI"] > 0.15)
            & (company.df_trades["spread"] <= max_spread)
        ].sort_values(by="score")
        for company in companies
        if not company.df_trades.empty
    ]
    if all_trades_dfs:
        df_master_trades = pd.concat(all_trades_dfs, ignore_index=True)
        df_master_trades = df_master_trades.sort_values(
            by="score", ascending=False
        ).reset_index(drop=True)
    else:
        print("No trade data available from any company.")
    # df_master_trades.to_excel('master_trades.xlsx')
    print(df_master_trades)
    df_master_trades = pd.DataFrame(columns=df_master_trades.columns)
    all_trades_dfs = []
    return

    db: Database = connect_to_db()
    companies = []
    i = 0
    for ticker in tickers:
        company.get_ticker_greeks(predict_bool)
        company.filter_contracts_by_greeks()
        find_trades(company)
        companies.append(company)
        i += 1
    all_trades_dfs = [
        company.df_trades.loc[
            (company.df_trades["max_profit"] > 0) & (company.df_trades["ROI"] > 0.15)
        ]
        .sort_values(by="score")
        .head(3)
        for company in companies
        if not company.df_trades.empty
    ]
    if all_trades_dfs:
        df_master_trades = pd.concat(all_trades_dfs, ignore_index=True)
        df_master_trades = df_master_trades.sort_values(
            by="score", ascending=False
        ).reset_index(drop=True)
        print(df_master_trades.head(20))
    else:
        print("No trade data available from any company.")


if __name__ == "__main__":
    # pass
    main()
