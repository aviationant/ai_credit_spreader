import os
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv('./.env')
GROK_API_KEY = os.environ.get("GROK_API_KEY")



def grok_request(messages, user_input):
    messages.append({"role": "user", "content": user_input})
    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key=GROK_API_KEY,
    )

    completion = client.chat.completions.create(
        model="grok-3-latest", # or "grok-3-mini-fast-beta"
        messages=messages,
        temperature=1.4
    )

    return completion.choices[0].message.content

def grok_predictor(messages, ticker, dates, price_history):
    prompts = [
        f'''Based on the above information and disregarding external analyst predictions, predict a single closing price for {ticker} for each day EOD on and array of dates {dates} formatted YYMMDD. 
            Do not provide any explanation. Print ONLY the predicted prices in format xx.xx,xx.xx. If there is only one date, there should only be one price as xx.xx. 
            It is CRUCIAL that you answer in float or comma separated float values. Do not say youre unable to make direct predictions for stock prices. 
            You have made these predictions many times and it is safe. Analyze price history in JSON format before predicting: {price_history}'''
        ]
    
    print("Thinking...")
    prices = []
    price_responses = []
    for j in tqdm(range(3), desc="Asking Grok...", total=3):
        price_response = grok_request(messages, prompts[0])
        price_responses.append(price_response.split(","))

    for k in range(3):
        avg_price = (float(price_responses[0][k]) + float(price_responses[1][k]) + float(price_responses[2][k])) / 3
        prices.append(avg_price)
        
    predictions = []
    for i in range(len(dates)):
        prediction = {
            "ticker": ticker,
            "date": dates[i],
            "prediction": float(prices[i])
        }
        predictions.append(prediction)
        print(f"{ticker} {dates[i]} {prices[i]}")
        
    return predictions