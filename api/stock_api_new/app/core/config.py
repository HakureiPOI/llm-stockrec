import os
from pydantic import BaseModel
from dotenv import load_dotenv

# 会自动读取项目根目录的 .env（以你运行 uvicorn 的目录为基准）
load_dotenv()


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "stock_api")
    api_prefix: str = os.getenv("API_PREFIX", "/v1")

    upstream_timeout_seconds: float = float(os.getenv("UPSTREAM_TIMEOUT_SECONDS", "5.0"))
    upstream_retries: int = int(os.getenv("UPSTREAM_RETRIES", "1"))

    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "60"))


settings = Settings()
