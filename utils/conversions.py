def convert_float(value: str):
    try:
        return float(value)
    except ValueError:
        return "Invalid input: cannot convert to float"
    
def clean_prices(response: str) -> list[float]:
    prices = response.split(",")
    for price in prices:
        price = convert_float(price)
    return prices