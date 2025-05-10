from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from tqdm import tqdm

load_dotenv("./.env")
OPENAI_API = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API)

messages = [
    {"role": "system", "content": "You are a sophisticated stock market analyst specializing in price prediction based on technical, fundemental, social, and political indicators."}
]

def gpt_web_search(user_input):
    messages.append({"role": "user", "content": user_input})
    response = client.responses.create(
        model="gpt-4o",
        tools=[{"type": "web_search_preview"}],
        input=user_input
    )
    gpt_response = response.output_text
    messages.append({"role": "assistant", "content": gpt_response})

    return gpt_response

def gpt_reasoning(user_input):
    messages.append({"role": "user", "content": user_input})
    response = client.responses.create(
        model="gpt-4o",
        reasoning={
            "summary": "auto"
            },
        input=messages
    )
    gpt_response = response.output_text
    messages.append({"role": "assistant", "content": gpt_response})

    return gpt_response

def gpt_predictor(ticker, date):
    prompts = [
        f"What is the current price of {ticker}?",
        f"Search the web for {ticker}  90 day price history and output weekly highs and lows.",
        f"Search the web for any industry news that pertains to {ticker}, including social an political events that could impact the stock sentiment.",
        f"Based on the above information and disregarding external analyst predictions, predict a single closing price for {ticker} EOD on date {date} formatted YYMMDD. Do not provide any explanation. Print ONLY the predicted price in format $xx.xx."
    ]

    print("Getting current price...")
    gpt_web_search(prompts[0])

    print("Getting price history...")
    gpt_web_search(prompts[1])

    print("Studying recent events...")
    gpt_web_search(prompts[2])

    print("Thinking...")
    prediction = gpt_reasoning(prompts[3])

    print(f"{ticker} {date} {prediction}")
    
    return prediction