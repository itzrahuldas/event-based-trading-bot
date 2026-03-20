import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import structlog

from src.database import Price
from src.utils.time import normalize_to_utc, round_to_15m
from src.constants import TimeFrame
from src.utils.rate_limiter import RateLimiter
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.database import SessionLocal # Using factory
import warnings

logger = structlog.get_logger()

class DataFetcher:
    def __init__(self, db: Session):
        self.db = db

    def _fetch_single_ticker_safe(self, ticker: str, period: str, interval: str, session_factory) -> dict:
        """
        Worker function to fetch one ticker.
        Safe: Handles Exceptions, Timeout, and uses own DB session.
        """
        result = {"ticker": ticker, "status": "FAILED", "rows": 0}
        
        # Create dedicated session for this thread
        db = session_factory()
        try:
            # 1. Fetch from yfinance (with potential internal retries in yf, but we add our own if needed)
            # Using progress=False to reduce noise
            df = yf.download(ticker, period=period, interval=interval, progress=False, ignore_tz=False, auto_adjust=True)
            
            if df.empty:
                result["status"] = "EMPTY"
                return result

            # Multi-index fix
            if isinstance(df.columns, pd.MultiIndex):
                try:
                    df = df.xs(ticker, axis=1, level=0)
                except:
                    pass

            # UTC Normalize
            if df.index.tz is None:
                # Assume exchange local -> UTC mapping is needed. For now, strict assumption:
                df.index = df.index.tz_localize("Asia/Kolkata").tz_convert("UTC")
            else:
                df.index = df.index.tz_convert("UTC")

            # 2. Upsert Logic (Idempotent)
            new_records = 0
            for ts, row in df.iterrows():
                ts_utc = ts.to_pydatetime()
                
                # Check exist (Optimization: Could load all existing timestamps for ticker first)
                exists = db.query(Price).filter_by(
                    ticker=ticker, 
                    timestamp=ts_utc, 
                    interval=interval
                ).first()
                
                if not exists:
                    # Robust check for NaNs
                    if pd.isna(row['Close']): continue

                    p = Price(
                        ticker=ticker,
                        timestamp=ts_utc,
                        interval=interval,
                        open=float(row['Open']),
                        high=float(row['High']),
                        low=float(row['Low']),
                        close=float(row['Close']),
                        volume=float(row['Volume'])
                    )
                    db.add(p)
                    new_records += 1
            
            db.commit()
            result["status"] = "SUCCESS"
            result["rows"] = new_records
            return result

        except Exception as e:
            db.rollback()
            result["error"] = str(e)
            return result
        finally:
            db.close()

    def fetch_batch_history(self, tickers: List[str], period: str = "60d", interval: str = "15m", max_workers: int = 5) -> dict:
        """
        Fetch batch of tickers in paralell with rate limiting and chunking.
        """
        # Configurable constants
        CHUNK_SIZE = 20
        limiter = RateLimiter(max_calls=10, period=1) # 10 calls per second

        summary = {"total": len(tickers), "success": 0, "failed": 0, "details": []}
        
        # Disable yfinance print noise
        warnings.filterwarnings("ignore")

        # Chunking
        for i in range(0, len(tickers), CHUNK_SIZE):
            chunk = tickers[i:i + CHUNK_SIZE]
            logger.info("fetch_batch_chunk", start=i, count=len(chunk))
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {}
                for ticker in chunk:
                    limiter.acquire() # Rate Limit
                    fut = executor.submit(self._fetch_single_ticker_safe, ticker, period, interval, SessionLocal)
                    futures[fut] = ticker
                
                for fut in as_completed(futures):
                    res = fut.result() # Will not throw, as worker catches Exception
                    summary["details"].append(res)
                    if res["status"] == "SUCCESS":
                        summary["success"] += 1
                        if res["rows"] > 0:
                            logger.info("fetch_success", ticker=res["ticker"], rows=res["rows"])
                    else:
                        summary["failed"] += 1
                        logger.error("fetch_failed", ticker=res["ticker"], error=res.get("error", "Unknown"))

        return summary

    def fetch_yfinance_history(self, ticker: str, period: str = "5d", interval: str = "15m") -> dict:
        """
        Fetch history for a single ticker (Synchronous wrapper).
        """
        from src.database import SessionLocal
        return self._fetch_single_ticker_safe(ticker, period, interval, SessionLocal)

    def get_prices(self, ticker: str, days: int = 90) -> pd.DataFrame:
        """
        Retrieve prices from DB for strategy.
        """
        cutoff = datetime.now() - timedelta(days=days)
        q = self.db.query(Price).filter(
            Price.ticker == ticker,
            Price.timestamp >= cutoff
        ).order_by(Price.timestamp.asc())
        
        rows = q.all()
        if not rows:
            return pd.DataFrame()
            
        data = [{
            "Open": r.open,
            "High": r.high,
            "Low": r.low,
            "Close": r.close,
            "Volume": r.volume
        } for r in rows]
        
        idx = [r.timestamp for r in rows]
        df = pd.DataFrame(data, index=idx)
        return df
