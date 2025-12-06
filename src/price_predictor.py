from pymongo.database import Database
from api.mongo_api import get_db_predictions, add_db_items
#from api.openai_api import gpt_research
#from api.grok_api import grok_predictor
import pandas as pd
from datetime import date
from utils.conversions import convert_df_to_float

def check_if_predicted(ticker, today: date) -> bool:
    for index, contract in ticker.df_contracts.iterrows():
        if (today in ticker.df_predictions["date"].values and
            contract.expiry_date in ticker.df_predictions["expiry_date"].values
        ): continue
        else: return False
    return True

def predict_prices(ticker) -> None:
    #messages = gpt_research(ticker)
    #ticker.predictions = grok_predictor(messages, ticker)
    print("here")

def prediction_formatter(ticker, prices: list[float], today: str) -> list[dict]:
    predictions = []
    for i in range(len(ticker.unique_dates)):
        prediction = {
            "date": today,
            "current_price": ticker.last_trade,
            "ticker": ticker.ticker,
            "expiry_date": ticker.unique_dates[i],
            "prediction": prices[i]
        }
        predictions.append(prediction)
        ticker.df_contracts.loc[ticker.df_contracts["expiry_date"] == prediction["expiry_date"], "prediction"] = float(prices[i])
    return predictions

def price_predictor(ticker, db: Database) -> None:
    today: str = date.today().strftime("%Y-%m-%d")
    try:
        predictions: list = get_db_predictions(db, ticker)
        ticker.df_predictions = pd.DataFrame(predictions)
        convert_df_to_float(ticker.df_predictions)
        convert_df_to_float(ticker.df_contracts)
    except:
        print("Failed to get DB.")
    if check_if_predicted(ticker, today):
        predictions = []
        for index, prediction in ticker.df_predictions.iterrows():
            ticker.df_contracts.loc[ticker.df_contracts["expiry_date"] == prediction["expiry_date"], "prediction"] = prediction["prediction"]
            predictions.append(prediction)
    else:
        ticker.df_predictions = pd.DataFrame()
        research: list[dict] = gpt_research(ticker)
        prices = grok_predictor(research, ticker)
        predictions = prediction_formatter(ticker, prices, today)
        ticker.df_predictions = pd.DataFrame(predictions)
        convert_df_to_float(ticker.df_predictions)
        convert_df_to_float(ticker.df_contracts)
        add_db_items(db, ticker.df_predictions.to_dict('records'))