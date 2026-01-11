from pydantic import BaseModel, Field

class Meta(BaseModel):
    stock_code: str = Field(default="")
    symbol: str = Field(default="")
    start_date: str = Field(default="")
    end_date: str = Field(default="")
    interval: str = Field(default="")
    rows: int = Field(default=0)
