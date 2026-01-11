from __future__ import annotations

import numpy as np
import pandas as pd


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add:
      - MA_10, MA_50
      - Daily_Return
      - Volatility_20d
      - RSI (14) using simple rolling mean
    """
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()

    out["MA_10"] = out["Close"].rolling(window=10, min_periods=1).mean()
    out["MA_50"] = out["Close"].rolling(window=50, min_periods=1).mean()

    out["Daily_Return"] = out["Close"].pct_change()
    out["Volatility_20d"] = out["Daily_Return"].rolling(window=20, min_periods=1).std()

    delta = out["Close"].diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)

    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()
    avg_loss = avg_loss.replace(0, np.nan)

    rs = avg_gain / avg_loss
    out["RSI"] = 100 - (100 / (1 + rs))

    # Readability
    float_cols = out.select_dtypes(include=["float64", "float32"]).columns
    out[float_cols] = out[float_cols].round(4)

    return out
