from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from tqdm import tqdm
from datetime import datetime, timedelta

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
        tools=[{
            "type": "web_search_preview",
            "search_context_size": "high",
            }],
        input=user_input
    )
    gpt_response = response.output_text
    messages.append({"role": "assistant", "content": gpt_response})

    return gpt_response

def gpt_reasoning(user_input):
    messages.append({"role": "user", "content": user_input})
    response = client.responses.create(
        model="gpt-4o",
        input=messages,
        # temperature=1,
        # top_p=0.8
    )
    gpt_response = response.output_text
    print(gpt_response)
    messages.append({"role": "assistant", "content": gpt_response})

    return gpt_response

def gpt_research(ticker, dates):
    today = datetime.now()
    prompts = [
        f"Search the web for any industry news that pertains to {ticker}, including social an political events that could impact the stock sentiment.",
    ]

    print("Studying recent events...")
    gpt_web_search(prompts[0])
    
    return messages
