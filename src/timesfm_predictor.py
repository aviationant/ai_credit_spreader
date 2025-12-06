import yfinance as yf
import timesfm
import torch
# Fetch 2 years of data
print("GPUs:")
print(torch.cuda.is_available())
data = yf.download('AAPL', start='2025-07-13', end='2025-09-13')
prices = data['Close'].values  # ~504 trading days
tfm = timesfm.TimesFm(
    hparams=timesfm.TimesFmHparams(
        backend="gpu",
        per_core_batch_size=32,
        horizon_len=128,
        num_layers=50,
        use_positional_embedding=False,
        context_len=2048,
    ),
    checkpoint=timesfm.TimesFmCheckpoint(
        huggingface_repo_id="google/timesfm-2.0-500m-pytorch"),
)