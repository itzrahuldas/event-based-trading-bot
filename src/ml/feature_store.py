import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from src.database import get_db, Price
from src.strategies.indicators import calculate_indicators
from src.utils.logger import get_logger

logger = get_logger(__name__)

class FeatureStore:
    def __init__(self, db: Session):
        self.db = db

    def load_data(self, ticker: str, days: int = 365) -> pd.DataFrame:
        """Loads raw price data"""
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        q = self.db.query(Price).filter(
            Price.ticker == ticker,
            Price.timestamp >= cutoff
        ).order_by(Price.timestamp.asc())
        
        rows = q.all()
        if not rows: return pd.DataFrame()
        
        data = [{
            "Open": r.open, "High": r.high, "Low": r.low, "Close": r.close, "Volume": r.volume
        } for r in rows]
        df = pd.DataFrame(data, index=[r.timestamp for r in rows])
        return df

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates ML features (X) and Targets (y).
        Features: RSI, ATR, Moving Averages, Volatility.
        Target: 1 if Close(t+1) > Close(t), else 0 (Binary Classification).
        """
        # 1. Base Indicators (Reuse strategy logic)
        df = calculate_indicators(df)
        
        # 2. Advanced / ML-specific features
        # Lags
        df['return_1'] = df['Close'].pct_change(1)
        df['return_5'] = df['Close'].pct_change(5)
        df['volatility_5'] = df['return_1'].rolling(5).std()
        
        # Distance from MA
        df['dist_ema50'] = (df['Close'] - df['EMA_50']) / df['EMA_50']
        
        # RSI Normalized
        df['rsi_norm'] = df['RSI'] / 100.0
        
        # 3. Target Generation (Forward looking)
        # Target: Next Candle Return > 0 (Simple Direction)
        # Shift -1 to align "Current Features" with "Next Return"
        df['next_return'] = df['Close'].shift(-1).pct_change(1) # This is actually curr/prev. 
        # Correct logic: Return of (t+1) vs (t).
        df['fwd_close'] = df['Close'].shift(-1)
        df['target_reg'] = (df['fwd_close'] - df['Close']) / df['Close']
        df['target_class'] = (df['target_reg'] > 0).astype(int) # 1 if Up, 0 if Down
        
        # Drop NaNs created by rolling/shifting
        df.dropna(inplace=True)
        
        return df

    def get_training_set(self, tickers: list, days: int = 365):
        """
        Aggregates data for multiple tickers into a single dataset.
        """
        all_dfs = []
        for ticker in tickers:
            raw = self.load_data(ticker, days=days)
            if len(raw) < 50: continue
            
            processed = self.create_features(raw)
            processed['ticker'] = ticker # Keep track
            all_dfs.append(processed)
            
        if not all_dfs: return pd.DataFrame()
        
        return pd.concat(all_dfs)
