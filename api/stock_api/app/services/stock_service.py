from __future__ import annotations

from typing import Any, Dict, List, Union

import pandas as pd
from datetime import datetime

from app.schemas.common import Meta
from app.schemas.stock import StockResponse
from app.services.akshare_client import fetch_zh_a_daily, normalize_symbol
from app.services.features import add_technical_indicators
from app.services.serializer import sanitize_for_json
from app.utils.interval import calc_date_range

# Optional cache
from app.utils.cache import TTLCache, cache_ttl_from_env

_cache = TTLCache(ttl_seconds=cache_ttl_from_env(60))


IntervalType = Union[str, int, None]


def _make_cache_key(symbol: str, interval_norm: str) -> str:
    return f"{symbol}:{interval_norm}"


def get_stock_data_with_features(stock_code: str, interval: IntervalType = "365d") -> StockResponse:
    start_date, end_date, interval_norm = calc_date_range(interval)
    symbol = normalize_symbol(stock_code)

    if not symbol:
        return StockResponse(
            success=False,
            message="Error: stock_code cannot be empty.",
            meta=Meta(stock_code=stock_code, symbol="", start_date=start_date, end_date=end_date, interval=interval_norm, rows=0),
            data=[],
            warnings=["empty_stock_code"],
        )

    # Cache hit
    ck = _make_cache_key(symbol, interval_norm)
    cached = _cache.get(ck)
    if cached is not None:
        return cached

    df: pd.DataFrame = fetch_zh_a_daily(symbol=symbol, start_date=start_date, end_date=end_date)

    if df.empty:
        resp = StockResponse(
            success=False,
            message=f"No data found for stock {symbol}.",
            meta=Meta(stock_code=stock_code, symbol=symbol, start_date=start_date, end_date=end_date, interval=interval_norm, rows=0),
            data=[],
            warnings=["no_data"],
        )
        _cache.set(ck, resp)
        return resp

    df = add_technical_indicators(df)

    records: List[Dict[str, Any]] = df.reset_index().to_dict(orient="records")
    records = sanitize_for_json(records)

    resp = StockResponse(
        success=True,
        message=f"Successfully retrieved stock data for {symbol}",
        meta=Meta(
            stock_code=stock_code,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=interval_norm,
            rows=len(records),
        ),
        data=records,
        warnings=[],
    )

    _cache.set(ck, resp)
    return resp

# ---------------------------------------------

def _is_valid_date(s: str) -> bool:
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except Exception:
        return False


def get_stock_data_with_features_by_dates(stock_code: str, start_date: str, end_date: str) -> StockResponse:
    symbol = normalize_symbol(stock_code)

    if not symbol:
        return StockResponse(
            success=False,
            message="Error: stock_code cannot be empty.",
            meta=Meta(stock_code=stock_code, symbol="", start_date=start_date, end_date=end_date, interval="", rows=0),
            data=[],
            warnings=["empty_stock_code"],
        )

    if not (_is_valid_date(start_date) and _is_valid_date(end_date)):
        return StockResponse(
            success=False,
            message="Error: start_date/end_date must be in YYYY-MM-DD format.",
            meta=Meta(stock_code=stock_code, symbol=symbol, start_date=start_date, end_date=end_date, interval="", rows=0),
            data=[],
            warnings=["invalid_date_format"],
        )

    if start_date > end_date:
        return StockResponse(
            success=False,
            message="Error: start_date must be <= end_date.",
            meta=Meta(stock_code=stock_code, symbol=symbol, start_date=start_date, end_date=end_date, interval="", rows=0),
            data=[],
            warnings=["invalid_date_range"],
        )

    df = fetch_zh_a_daily(symbol=symbol, start_date=start_date, end_date=end_date)

    if df.empty:
        return StockResponse(
            success=False,
            message=f"No data found for stock {symbol} in the given date range.",
            meta=Meta(stock_code=stock_code, symbol=symbol, start_date=start_date, end_date=end_date, interval="", rows=0),
            data=[],
            warnings=["no_data"],
        )

    df = add_technical_indicators(df)

    records = df.reset_index().to_dict(orient="records")
    records = sanitize_for_json(records)

    return StockResponse(
        success=True,
        message=f"Successfully retrieved stock data for {symbol}",
        meta=Meta(stock_code=stock_code, symbol=symbol, start_date=start_date, end_date=end_date, interval="", rows=len(records)),
        data=records,
        warnings=[],
    )
