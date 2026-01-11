from fastapi import APIRouter, Query

from app.schemas.stock import StockRequest, StockResponse

from app.services.stock_service import (
    get_stock_data_with_features,
    get_stock_data_with_features_by_dates,
)

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.get("/{stock_code}", response_model=StockResponse)
def get_stock(
    stock_code: str,
    interval: str = Query("365d", description="e.g. 30d / 6m / 1y / 365"),
):
    return get_stock_data_with_features(stock_code=stock_code, interval=interval)

@router.get("/{stock_code}/range", response_model=StockResponse)
def get_stock_range(
    stock_code: str,
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
):
    return get_stock_data_with_features_by_dates(
        stock_code=stock_code, start_date=start_date, end_date=end_date
    )


@router.post("", response_model=StockResponse)
def post_stock(req: StockRequest):
    return get_stock_data_with_features(stock_code=req.stock_code, interval=req.interval)
