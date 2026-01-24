from templates.df_templates import get_df_template
from api.nasdaq_api import get_contract_list, get_price_history, get_greeks
import pandas as pd
from prediction.price_predictor import price_predictor
from prediction.direction_predict import get_direction
from utils.fetch_data import fetch_data
from tqdm.contrib.concurrent import thread_map
from datetime import datetime
import json
import re
import os

companies_array = []

DELTA_MAX = float(os.environ.get("DELTA_MAX"))
DELTA_MIN = float(os.environ.get("DELTA_MIN"))

class Company:
    def __init__(self, ticker: str) -> None:
        self.ticker: str = ticker
        self.df_contracts: pd.DataFrame = get_df_template("contracts")
        self.last_trade: float = 0.0
        self.df_prices: pd.DataFrame = get_df_template("price_history")
        self.df_trades: pd.DataFrame = get_df_template("trades")
        self.expiry_dates: list[str] = []
        self.earnings_date: str
        self.direction: str = ""
        self.dir_streak: int = 0

    def get_price_data(self) -> None:
        price_columns = ["open", "high", "low", "close"]
        get_contract_list(self)
        data = get_price_history(self)
        data_json = json.loads(data)
        df = pd.DataFrame.from_dict(data_json["data"]["tradesTable"]["rows"])
        df[price_columns] = df[price_columns].replace({r'\$': ''}, regex=True)
        df[price_columns] = df[price_columns].replace({r'\,': ''}, regex=True)
        self.df_prices = df[price_columns].apply(pd.to_numeric)
        
    def get_expiry_dates(self) -> None:
        expiry_dates = self.df_contracts.expiry_date.unique().tolist()
        i = len(expiry_dates)-1
        if not self.earnings_date:
            self.expiry_dates = expiry_dates
            return
        earn_date_obj = datetime.strptime(self.earnings_date, "%b %d, %Y")
        while i >= 0:
            date_obj = datetime.strptime(expiry_dates[i], "%y%m%d")
            if date_obj > earn_date_obj:
                expiry_dates.pop(i)
            i -= 1
        self.expiry_dates = expiry_dates
    
    def get_earnings_date(self) -> None:
        url_earnings = f'https://api.nasdaq.com/api/analyst/{self.ticker}/earnings-date'
        data = json.loads(fetch_data(url_earnings))
        earnings_string = data.get('data', {}).get('announcement')
        earnings_date = re.search(r"Earnings announcement\* for \S+: (\S+ [0-9]{1,2}, [0-9]{4})", earnings_string)
        self.earnings_date = earnings_date.group(1)

    def get_greeks(self) -> None:
            for date in self.expiry_dates:
                get_greeks(self)

    def filter_contracts_by_greeks(self) -> None:
        self.df_contracts = self.df_contracts[
            (abs((self.df_contracts['delta'])) >= DELTA_MIN) &
            (abs((self.df_contracts['delta'])) <= DELTA_MAX)
            ].reset_index(drop=True)

    def build_df_row(self, df_companies, SMA_fast_slope, SMA_slow_slope, dir_streak) -> None:
        df_companies.loc[len(df_companies)] = [
            self.ticker,
            self.last_trade,
            self.direction,
            self.expiry_dates,
            self.earnings_date,
            round(SMA_fast_slope, 3),
            round(SMA_slow_slope, 3),
            dir_streak
        ]



def build_companies_df(companies, predict_bool):
    df_companies = get_df_template("companies")
    companies_array = []

    def task_fetch_prices(company):
        try:
            current_comp = Company(company)
            current_comp.get_price_data()
            try:
                current_comp.get_earnings_date()
            except:
                current_comp.earnings_date = ""
            companies_array.append(current_comp)
        except: return

    thread_map(task_fetch_prices, companies, max_workers=20, desc=f"Fetching data...",
                    ascii=True, colour="#327DA0")
    for current_comp in companies_array:
        try:
            current_comp.get_expiry_dates()
            if predict_bool == "True":
                [current_comp.direction,
                SMA_fast_slope,
                SMA_slow_slope,
                current_comp.dir_streak] = get_direction(current_comp.df_prices)
            else: current_comp.direction = "bull"
            current_comp.build_df_row(df_companies, SMA_fast_slope, SMA_slow_slope, current_comp.dir_streak)
        except: continue    
        df_companies = df_companies.sort_values(by="dir_streak", ascending=False).reset_index(drop=True)
    # print(df_companies[
    #     (df_companies["direction"] != "none") & 
    #     (df_companies["expiry_dates"].str.len() > 0) &
    #     (df_companies["dir_streak"] >= 12) &
    #     (df_companies["dir_streak"] <= 33)].head(40))
    return companies_array, df_companies