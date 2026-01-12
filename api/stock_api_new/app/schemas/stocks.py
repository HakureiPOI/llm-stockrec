from __future__ import annotations 
from datetime import date 
from typing import Literal 

from pydantic import BaseModel, Field 

Interval = Literal['7d', '30d', '365d', '3m', '6m', '1y']
Adjust = Literal["", "qfq", "hfq"]

class Candle(BaseModel):
    date: date
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: int | None = Field(default=None, ge=0)

class CandleMeta(BaseModel):
    stock_code : str 
    interval : Interval 
    start : date 
    end : date 
    rows : int 

class CandleResponse(BaseModel):
    success : bool = True 
    message : str = 'ok'
    meta : CandleMeta
    data : list[Candle]

