import sys
from io import StringIO
from chronos_test import predictor

ticker = "NVDA"

for i in range(10):
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    direction = predictor(ticker)
    sys.stdout = old_stdout
    print(f"{ticker} - {direction}")