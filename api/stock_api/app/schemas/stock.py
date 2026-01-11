from typing import Any, Dict, List, Union

from pydantic import BaseModel, Field

from app.schemas.common import Meta

class StockRequest(BaseModel):
    stock_code: str = Field(..., examples=["600519", "000001", "600519.SH"])
    interval: Union[str, int] = Field("365d", examples=["30d", "6m", "1y", 365])

class StockResponse(BaseModel):
    success: bool
    message: str
    meta: Meta
    data: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
