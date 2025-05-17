from pymongo.database import Database
from api.mongo_api import get_db_predictions, add_db_items
from api.openai_api import gpt_research
from api.grok_api import grok_predictor
import pandas as pd
from datetime import date

def check_if_predicted(ticker, today: date) -> bool:
    if today in ticker.df_predictions["date"].values and ticker.ticker in ticker.df_predictions["ticker"].values:
        return True
    else: return False

def predict_prices(ticker) -> None:
    messages = gpt_research(ticker)
    ticker.predictions = grok_predictor(messages, ticker)

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
    return predictions

def price_predictor(ticker, db: Database) -> None:
    today: str = date.today().strftime("%Y-%m-%d")
    try:
        predictions: list = get_db_predictions(db)
        ticker.df_predictions = pd.DataFrame(predictions)
    except:
        print("Failed to get DB.")
    if check_if_predicted(ticker, today):
        predictions = [row for index, row in ticker.df_predictions.iterrows() if row["ticker"] == ticker]
    else:
        ticker.df_predictions = pd.DataFrame()
        research: list[dict] = gpt_research(ticker)
        prices = grok_predictor(research, ticker)
        predictions = prediction_formatter(ticker, prices, today)
        ticker.df_predictions = pd.DataFrame(predictions)
        add_db_items(db, ticker.df_predictions.to_dict('records'))