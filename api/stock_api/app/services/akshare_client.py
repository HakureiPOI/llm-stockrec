from __future__ import annotations

import pandas as pd

try:
    import akshare as ak
except ImportError as e:
    raise ImportError(f"Missing dependency: {e}. Please install akshare.")


def normalize_symbol(stock_code: str) -> str:
    """
    Accept: "600519", "600519.SH", "600519.SZ" -> "600519"
    """
    if stock_code is None:
        return ""
    return str(stock_code).strip().split(".")[0].strip()


def fetch_zh_a_daily(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch A-share daily hist data via AkShare, return standardized OHLCV dataframe
    indexed by Date with columns: Open, High, Low, Close, Volume.
    start_date/end_date: YYYY-MM-DD
    """
    if not symbol:
        return pd.DataFrame()

    start_date_clean = start_date.replace("-", "")
    end_date_clean = end_date.replace("-", "")

    try:
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date_clean,
            end_date=end_date_clean,
            adjust="qfq",
        )
    except Exception as e:
        # Never raise to API layer
        print(f"[AkShare Error] symbol={symbol} start={start_date} end={end_date} err={e}")
        return pd.DataFrame()

    if df is None or df.empty:
        return pd.DataFrame()

    rename_map = {
        "日期": "Date",
        "开盘": "Open",
        "最高": "High",
        "最低": "Low",
        "收盘": "Close",
        "成交量": "Volume",
    }

    existing = [c for c in rename_map.keys() if c in df.columns]
    if not existing:
        print(f"[Column Error] AkShare returned columns={list(df.columns)}")
        return pd.DataFrame()

    df = df[existing].rename(columns=rename_map)

    required = {"Date", "Open", "High", "Low", "Close", "Volume"}
    if not required.issubset(df.columns):
        print(f"[Column Error] missing required cols, got={list(df.columns)}")
        return pd.DataFrame()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).set_index("Date").sort_index()

    # Ensure numeric
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Close"])
    return df
