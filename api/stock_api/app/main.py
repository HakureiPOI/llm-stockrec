from fastapi import FastAPI
from fastapi import Response
from dotenv import load_dotenv

from app.routers.health import router as health_router
from app.routers.stocks import router as stocks_router

load_dotenv()

app = FastAPI(
    title="China Stock Data API",
    version="1.0.0",
)

app.include_router(health_router)
app.include_router(stocks_router)

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)