from __future__ import annotations 

from datetime import date, timedelta 
from typing import Annotated, Literal 

from fastapi import APIRouter, Path, Query, HTTPException, Response

from app.schemas.stocks import Candle, CandleMeta, CandleResponse, Interval, Adjust
from app.providers.akshare_provider import AkShareProvider
from app.core.cache import TTLCache 
from app.core.config import settings


router = APIRouter(prefix='/stocks', tags=['stocks'])

_cache = TTLCache(ttl_seconds=settings.cache_ttl_seconds)



# def _fake_candles(start: date, end: date) -> list[Candle]:
#     out: list[Candle] = []
#     cur = start
#     price = 10.0
#     while cur <= end:
#         # 只生成工作日数据也行，这里简单起见每天一条
#         open_ = price
#         close = price * 1.001
#         high = max(open_, close) * 1.002
#         low = min(open_, close) * 0.998
#         out.append(
#             Candle(
#                 date=cur,
#                 open=round(open_, 2),
#                 high=round(high, 2),
#                 low=round(low, 2),
#                 close=round(close, 2),
#                 volume=100000,
#             )
#         )
#         price = close
#         cur += timedelta(days=1)
#     return out

@router.get("/{stock_code}/candles",
            response_model=CandleResponse,
            response_model_exclude_none=True)
def get_candles(
    response : Response,
    stock_code : Annotated[str, Path(min_length=6, max_length=6, pattern=r'\d{6}')],
    interval : Annotated[Interval, Query(description='Data window preset')] ='30d',
    start : Annotated[date | None, Query(description='YYYY--MM--DD')] = None, 
    end : Annotated[date | None, Query(description='YYYY--MM--DD')] = None, 
    limit : Annotated[int, Query(ge=1, le=2000)] = 1000,
    adjust: Annotated[Adjust, Query(description="Price adjustment: '' | qfq | hfq")] = "",
    fields: Annotated[str | None, Query(description="Comma-separated fields: date,open,high,low,close,volume")] = None,
) -> CandleResponse:
    # 当 start/end 为空的时候，根据 interval 给出区间 
    today = date.today() 

    # 这个逻辑之后需要优化一下，不应该限制 inteval
    if start is None or end is None:
        end = today
        if interval == '7d':
            start = end - timedelta(days=7)
        elif interval == "30d":
            start = end - timedelta(days=30)
        elif interval == '3m':
            start = end - timedelta(days=92)
        elif interval == "6m":
            start = end - timedelta(days=183)
        elif interval in ("1y", "365d"):
            start = end - timedelta(days=365)

    # 逻辑校验 
    assert start is not None and end is not None 

    if start > end:
        raise HTTPException(status_code=400, detail='start must be <= end')

    if stock_code == '000000':
        raise HTTPException(status_code=404, detail='stock not found')

    fields_key = fields or "ALL"
    cache_key = (
        f"candles:{stock_code}:"
        f"start={start.isoformat()}:end={end.isoformat()}:"
        f"interval={interval}:adjust={adjust}:limit={limit}:fields={fields_key}"
    )

    cached = _cache.get(cache_key)

    # 缓存命中直接返回
    if cached is not None:
        response.headers['X-Cache'] = 'HIT'
        return cached

    response.headers["X-Cache"] = "MISS"

    df = AkShareProvider.get_a_stock_daily(stock_code, start, end, adjust=adjust)

    # limit：取最近 limit 条（akshare 通常是按日期升序）
    df = df.sort_values("date").tail(limit)

    candles = [
        Candle(
            date=row["date"],
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=int(row["volume"]),
        )
        for _, row in df.iterrows()
    ]

    resp = CandleResponse(
        message=f"candles for {stock_code}",
        meta=CandleMeta(
            stock_code=stock_code,
            interval=interval,
            start=start,
            end=end,
            rows=len(candles),
        ),
        data=candles,
    )

    allowed = {"date", "open", "high", "low", "close", "volume"}

    def normalize_fields(s : str) -> list[str]:
        parts = [p.strip().lower() for p in s.split(",") if p.strip()]
        parts = sorted(set(parts))
        return parts

    wanted = None
    fields_key = "ALL"
    if fields:
        wanted = normalize_fields(fields)
        if not wanted or any(f not in allowed for f in wanted):
            raise HTTPException(status_code=400, detail="invalid fields")
        fields_key = ",".join(wanted)

    cache_key = (
        f"candles:{stock_code}:"
        f"start={start.isoformat()}:end={end.isoformat()}:"
        f"interval={interval}:adjust={adjust}:limit={limit}:fields={fields_key}"
    )

    cached = _cache.get(cache_key)
    if cached is not None:
        response.headers["X-Cache"] = "HIT"
        return cached

    response.headers["X-Cache"] = "MISS"

    df = AkShareProvider.get_a_stock_daily(stock_code, start, end, adjust=adjust)
    df = df.sort_values("date").tail(limit)

    candles = [ 
        Candle( 
            date=row["date"], 
            open=float(row["open"]), 
            high=float(row["high"]), 
            low=float(row["low"]), 
            close=float(row["close"]), 
            volume=int(row["volume"]), 
            ) for _, row in df.iterrows() 
        ] 
            
    resp = CandleResponse( 
        message=f"candles for {stock_code}",
        meta=CandleMeta( 
            stock_code=stock_code, 
            interval=interval,
            start=start, 
            end=end, 
            rows=len(candles), 
            ), 
        data=candles, 
        )

    resp_dict = resp.model_dump()
    if wanted is not None:
        resp_dict["data"] = [{k: item[k] for k in wanted} for item in resp_dict["data"]]

    _cache.set(cache_key, resp_dict)

    return resp_dict
