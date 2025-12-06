from dotenv import load_dotenv
load_dotenv("./.env")
from pymongo.database import Database
from src.trade_finder import find_trades
from src.classes.ticker_class import Ticker
from api.mongo_api import connect_to_db
import os


ticker_string = os.environ.get("TICKERS")
tickers = ticker_string.split(",")

print(ticker_string)

def main():
    db: Database = connect_to_db()
    companies = []
    i=0
    for ticker in tickers:
        company = Ticker(ticker, db)
        company.get_price_data()
        company.get_unique_dates()
        company.get_predictions(db)
        company.filter_contracts_by_prediction()
        company.get_ticker_greeks()
        company.filter_contracts_by_greeks()
        find_trades(company)
        companies.append(company)
        i+=1
    for company in companies:
        if not company.df_trades.empty:
            print(company.df_trades)    

if __name__ == "__main__":
    # pass
    main()
