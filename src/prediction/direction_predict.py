from dotenv import load_dotenv
load_dotenv("./.env")
import pandas as pd
from tech_analysis.signals import calc_sma_slope, calc_streak
import os

sma_fast_period = os.environ.get("SMA_FAST_PERIOD")
sma_slow_period = os.environ.get("SMA_SLOW_PERIOD")

def get_direction(price_history):
    sma_fast_slope = calc_sma_slope(price_history, sma_fast_period)
    sma_slow_slope = calc_sma_slope(price_history, sma_slow_period)
    [direction, direction_streak] = calc_streak(price_history)

    if (direction == "bull" and sma_fast_slope > 1 and sma_slow_slope > 1):
        prediction = "bull"
    elif (direction == "bear" and sma_fast_slope < 1 and sma_slow_slope < 1):
        prediction = "bear"
    else: prediction = "none"

    return [prediction, sma_fast_slope, sma_slow_slope, direction_streak]