from __future__ import annotations

from datetime import date
import pandas as pd
import akshare as ak
import concurrent.futures
import time
from fastapi import HTTPException

from app.core.config import settings


def _fmt(d: date) -> str:
    # akshare 多数接口喜欢 YYYYMMDD
    return d.strftime("%Y%m%d")


def run_with_timeout_and_retry(fn, *, timeout_s: float, retries: int):
    last_exc = None
    for i in range(retries + 1):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(fn)
                return fut.result(timeout=timeout_s)
        except concurrent.futures.TimeoutError:
            last_exc = TimeoutError("upstream timeout")
        except Exception as e:
            last_exc = e

        time.sleep(0.2 * (i + 1))

    raise last_exc



class AkShareProvider:
    """
    只负责：从 akshare 拿数据 + 转成需要的列
    """

    @staticmethod
    def get_a_stock_daily(stock_code : str, start: date, end : date, adjust : str) -> pd.DataFrame:
        """
        返回列：date, open, high, low, close, volume
        """
        try:
            def _call():
                return ak.stock_zh_a_hist(
                    symbol=stock_code,
                    period="daily",
                    start_date=_fmt(start),
                    end_date=_fmt(end),
                    adjust=adjust,
                )

            df = run_with_timeout_and_retry(
                _call, 
                timeout_s=settings.upstream_timeout_seconds, 
                retries=settings.upstream_retries,
                )

        except Exception as e:
            raise HTTPException(status_code=502, detail=f"upstream akshare error: {type(e).__name__}")


        if df is None or df.empty:
            # 没数据：可以视为资源不存在或时间范围无数据
            # 这里先用 404
            raise HTTPException(status_code=404, detail="no data for given stock/time range")

        # akshare 返回常见中文列名：日期/开盘/收盘/最高/最低/成交量（不同版本可能略有差异）
        colmap_candidates = {
            "日期": "date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
        }

        # 只取存在的列并重命名
        cols_present = {k: v for k, v in colmap_candidates.items() if k in df.columns}
        df = df[list(cols_present.keys())].rename(columns=cols_present)

        # 类型整理
        df["date"] = pd.to_datetime(df["date"]).dt.date
        for c in ["open", "high", "low", "close"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0).astype(int)

        # 去掉无效行
        df = df.dropna(subset=["date", "open", "high", "low", "close"])
        if df.empty:
            raise HTTPException(status_code=404, detail="no usable data after cleaning")

        return df
