import requests
import random
import time
from typing import Optional

# List of common real-world User-Agents (updated for 2025, mostly Chrome/Edge/Firefox on Windows/macOS)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5; rv:136.0) Gecko/20100101 Firefox/136.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Edg/141.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
]

# Possible Accept-Language variations
ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.9",
    "en-US,en;q=0.8",
    "de-DE,de;q=0.9,en;q=0.8",
]

# Possible referers (optional, adds realism sometimes)
REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    None,  # No referer sometimes
]

def fetch_data(url: str, session: Optional[requests.Session] = None, min_delay: float = 0.1, max_delay: float = 0.3) -> Optional[str]:
    """
    Fetches data from the URL with randomized headers and delay.
    Use a shared session for multiple calls to reuse connections.
    """
    # Random delay before request (mimic human pauses)
    time.sleep(random.uniform(min_delay, max_delay))
    
    # Create or use session
    own_session = session is None
    s = session or requests.Session()
    
    # Randomize headers
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": random.choice(ACCEPT_LANGUAGES),
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": random.choice(["same-origin", "same-site", "cross-site"]),
    }
    
    # Occasionally add a Referer for more realism
    if random.random() > 0.5:
        referer = random.choice(REFERERS)
        if referer:
            headers["Referer"] = referer
    
    try:
        response = s.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {url}: {e}")
        # Simple retry (up to 3 times) with backoff
        for attempt in range(3):
            time.sleep(2 ** attempt * random.uniform(1, 2))  # Exponential + jitter
            try:
                response = s.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                return response.text
            except:
                pass
        print(f"Failed after retries: {url}")
        return None
    finally:
        if own_session:
            s.close()