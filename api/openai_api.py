from openai import OpenAI
import os

OPENAI_API = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API)

def gpt_web_search(user_input: str, messages: list[str]) -> None:
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

def gpt_research(ticker) -> list[str]:
    messages = [
        {"role": "system", "content": "You are a sophisticated stock market analyst specializing in price prediction based on technical, fundemental, social, and political indicators."}
    ]
    prompts = [
        f"Search the web for any industry news that pertains to {ticker.ticker}, including social an political events that could impact the stock sentiment.",
    ]

    print("Studying recent events...")
    gpt_web_search(prompts[0], messages)
    
    return messages