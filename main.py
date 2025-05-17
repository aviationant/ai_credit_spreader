from pymongo.database import Database
from src.trade_finder import find_trades
from src.classes.ticker_class import Ticker
from api.mongo_api import connect_to_db
from dotenv import load_dotenv
import os

load_dotenv("./.env")
ticker_string = os.environ.get("TICKERS")
tickers = ticker_string.split(",")

def main():
    db: Database = connect_to_db()
    companies = []
    for ticker in tickers:
        company = Ticker(ticker, db)
        company.get_price_data()
        company.get_unique_dates()
        company.get_predictions(db)
        find_trades(company)
        companies.append(company)

if __name__ == "__main__":
    # pass
    main()
