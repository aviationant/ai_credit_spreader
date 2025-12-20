# chronos_multi_gpu_csv_batch.py
# Multi-GPU Chronos-T5-large forecasting from real CSV files
# Uses both GTX 1070s via DataParallel — maxes 16GB VRAM
# Designed for credit spread directional bias (45-day horizon)

import os
import torch
import pandas as pd
import time
from chronos import ChronosPipeline
from pathlib import Path

# Avoid memory fragmentation
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# ----------------------------- CONFIG -----------------------------
DEVICE = "cuda"
MODEL_NAME = "amazon/chronos-t5-large"
PREDICTION_LENGTH = 30
NUM_SAMPLES = 40          # Stable median + safe on dual 1070s
MAX_CONTEXT_DAYS = 126    # ~3 years of daily data — optimal for Chronos

# Folder containing your CSV files (Schwab exports)
CSV_FOLDER = Path("./historical_data")  # Change if needed, e.g. Path("/path/to/csvs")

# File pattern: supports both:
# - One CSV per ticker: AAPL.csv, SPY.csv, etc.
# - Or single CSV with 'Ticker' column
# ---------------------------------------------------------------

def print_gpu_utilization(label=""):
    if label:
        print(f"\n--- GPU Utilization: {label} ---")
    else:
        print("\n--- GPU Utilization Check ---")
    if torch.cuda.device_count() == 0:
        print("No GPUs detected")
        return
    for i in range(torch.cuda.device_count()):
        print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
        print(f"   Allocated: {torch.cuda.memory_allocated(i) / 1024**3:.2f} GB")
        print(f"   Reserved : {torch.cuda.memory_reserved(i) / 1024**3:.2f} GB")
    print(f"Current device: {torch.cuda.current_device()}")
    print("------------------------------------\n")

def predictor(ticker):
    print(f"Loading model: {MODEL_NAME}")
    print(f"Using DataParallel on {torch.cuda.device_count()} GPUs\n")

    pipeline = ChronosPipeline.from_pretrained(
        MODEL_NAME,
        device_map=DEVICE,
        dtype=torch.bfloat16,
        low_cpu_mem_usage=True,
    )

    # Multi-GPU setup
    if torch.cuda.device_count() > 1:
        print(f"Replicating model across {torch.cuda.device_count()} GPUs with DataParallel")
        pipeline.model = torch.nn.DataParallel(pipeline.model)
        pipeline.model.config = pipeline.model.module.config
        pipeline.model.device = pipeline.model.module.device
    else:
        print("Single GPU mode")

    print_gpu_utilization("After model load")

    # ------------------- Load real data from CSVs -------------------
    print(f"Loading historical data from: {CSV_FOLDER.resolve()}")

    contexts = []
    current_prices = []
    tickers = []

    if not CSV_FOLDER.exists():
        raise FileNotFoundError(f"CSV folder not found: {CSV_FOLDER}")

    # Case 1: Individual CSV per ticker (e.g., AAPL.csv)
    csv_files = list(CSV_FOLDER.glob(f"{ticker}_historical.csv"))
    print(csv_files)
    if csv_files:
        for csv_file in csv_files:
            ticker = csv_file.stem.upper()  # Filename without .csv
            try:
                df = pd.read_csv(csv_file, parse_dates=["date"])
                if "close" not in df.columns:
                    print(f"Skipping {csv_file} — no 'close' column")
                    continue
                # Sort by date and take last N days
                df = df.sort_values("date")
                closes = df["close"].dropna().values[-MAX_CONTEXT_DAYS:]
                if len(closes) < 100:
                    print(f"Skipping {ticker} — insufficient data ({len(closes)} points)")
                    continue
                contexts.append(torch.tensor(closes, dtype=torch.float32))
                current_prices.append(closes[-1])
                tickers.append(ticker)
                print(f"Loaded {ticker}: {len(closes)} days")
            except Exception as e:
                print(f"Error loading {csv_file}: {e}")

    # Case 2: Single CSV with 'Ticker' column (fallback)
    # else:
    #     # Look for any CSV and assume multi-ticker format
    #     potential_file = next(CSV_FOLDER.glob("*.csv"), None)
    #     if potential_file:
    #         df = pd.read_csv(potential_file, parse_dates=["cate"])
    #         required = {"ticker", "date", "close"}
    #         if required.issubset(df.columns):
    #             for ticker in df["Ticker"].unique():
    #                 sub_df = df[df["Ticker"] == ticker].sort_values("Date")
    #                 closes = sub_df["Close"].dropna().values[-MAX_CONTEXT_DAYS:]
    #                 if len(closes) >= 100:
    #                     contexts.append(torch.tensor(closes, dtype=torch.float32))
    #                     current_prices.append(closes[-1])
    #                     tickers.append(ticker)
    #                     print(f"Loaded {ticker}: {len(closes)} days")

    if not contexts:
        raise ValueError("No valid data loaded from CSVs. Check folder and format.")

    batch_context = torch.stack(contexts)
    print(f"\nLoaded {len(tickers)} tickers → Batch shape: {batch_context.shape}")

    # ------------------------- TIMED INFERENCE -------------------------
    print(f"Starting batched forecast: {PREDICTION_LENGTH} days, {NUM_SAMPLES} samples...")
    print_gpu_utilization("Before inference")

    start_time = time.time()

    forecast = pipeline.predict(
        batch_context,
        prediction_length=PREDICTION_LENGTH,
        num_samples=NUM_SAMPLES,
    )

    end_time = time.time()
    duration = end_time - start_time

    print_gpu_utilization("After inference")
    print(f"\nBATCH FORECAST COMPLETED IN {duration:.2f} SECONDS")
    print(f"Per-ticker avg: {duration / len(tickers):.3f}s (batched across {torch.cuda.device_count()} GPUs)\n")
    # -------------------------------------------------------------------

    # Directional bias
    medians = forecast.median(dim=0).values.cpu().numpy()
    final_medians = medians[:, -1]

    print("Directional Bias (45-day forecast):")
    print("-" * 80)
    for ticker, current, future in zip(tickers, current_prices, final_medians):
        change_pct = (future - current) / current * 100
        direction = "BULL" if change_pct > 0 else "BEAR"
        print(f"{ticker:8}: ${current:8.2f} → ${future:8.2f} ({change_pct:+6.2f}%) → {direction}")

    print("\nBoth GPUs are fully engaged — check nvidia-smi!")
    print("Next: Hook this into your live Schwab pull for daily screening.")

    return direction