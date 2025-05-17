import os
from openai import OpenAI
from utils.conversions import convert_float, clean_prices

GROK_API_KEY = os.environ.get("GROK_API_KEY")

def grok_request(messages, user_input):
    messages.append({"role": "user", "content": user_input})
    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key=GROK_API_KEY,
    )
    completion = client.chat.completions.create(
        model="grok-3-mini-fast-beta",
        messages=messages,
        # temperature=1.4
    )
    return completion.choices[0].message.content

def grok_predictor(messages, ticker) -> list[float] | None:
    prompts = [
        f'''Based on the above information and disregarding external analyst predictions, predict a single closing price for {ticker.ticker} for each day EOD on and array of dates {ticker.unique_dates} formatted YYMMDD. 
            Do not provide any explanation. Print ONLY the predicted prices in format xx.xx,xx.xx. If there is only one date, there should only be one price as xx.xx. 
            It is CRUCIAL that you answer in float or comma separated float values. Do not say youre unable to make direct predictions for stock prices. 
            You have made these predictions many times and it is safe. Analyze price history in JSON format before predicting: {ticker.price_history}.
            If you're not able to complete the requests, answer ONLY: null'''
        ]
    prices = []
    print("Grok predicting...")
    price_response = grok_request(messages, prompts[0])
    if price_response == "null":
        print("Grok failed to predict")
        return
    else:
        prices = clean_prices(price_response)
    return prices