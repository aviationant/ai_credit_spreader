from src.templates.df_templates import get_df_template
from api.nasdaq_api import get_contract_list, get_price_history, get_greeks
from api.mongo_api import add_db_items
import pandas as pd
from pymongo.database import Database
from src.price_predictor import price_predictor
import os

DELTA_MAX = os.environ.get("DELTA_MAX")
DELTA_MIN = os.environ.get("DELTA_MIN")

class Ticker:
    def __init__(self, ticker: str, db: Database) -> None:
        self.ticker: str = ticker
        self.df_contracts: pd.DataFrame = get_df_template("contracts")
        self.last_trade: float = 0.0
        self.price_history: str = ""
        self.unique_dates: list[str] = []
        self.df_predictions: pd.DataFrame = get_df_template("predictions")
        self.df_trades: pd.DataFrame = get_df_template("trades")
        self.db: Database = db

    def get_price_data(self) -> None:
        print("Gettting price data...")
        get_contract_list(self)
        get_price_history(self)
        
    def get_unique_dates(self) -> None:
        self.unique_dates = self.df_contracts.expiry_date.unique()

    def get_predictions(self, db: Database) -> None:
        price_predictor(self, db)

    def get_ticker_greeks(self) -> None:
        for index, prediction in self.df_predictions.iterrows():
            get_greeks(self, prediction)

    def filter_contracts(self) -> None:
        self.df_contracts = self.df_contracts[
            (abs((self.df_contracts['delta'].astype(float))) >= DELTA_MIN) &
            (abs((self.df_contracts['delta'].astype(float))) <= DELTA_MAX)
            ].reset_index(drop=True)