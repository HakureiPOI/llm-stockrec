from fastapi import APIRouter 
from app.api.v1.health import router as health_router 
from app.api.v1.stocks import router as stocks_router

api_router = APIRouter() 
api_router.include_router(health_router)
api_router.include_router(stocks_router)