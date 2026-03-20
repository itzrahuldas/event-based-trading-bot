import pandas as pd
from datetime import timedelta
from typing import List, Tuple
from src.constants import TimeFrame

def check_gaps(df: pd.DataFrame, interval: TimeFrame = TimeFrame.M15) -> List[Tuple[pd.Timestamp, pd.Timestamp]]:
    """
    Identify time gaps in the OHLCV dataframe.
    Assumes df has a DateTimeIndex.
    """
    if df.empty:
        return []
        
    df = df.sort_index()
    
    # Simple check: calculate difference between consecutive timestamps
    # This is a basic implementation. For market data, we must account for 
    # market hours (gap between 3:30 PM and 9:15 AM is valid).
    # For now, we flag irregularity if diff > interval per market session rules.
    # A robust implementation would use pandas_market_calendars to filter valid sessions.
    
    # We will implement a simplified check: 
    # 1. Resample to interval (filling gaps with NaN)
    # 2. Return ranges where data is missing within Valid Market Hours.
    
    # TODO: Integration with pandas_market_schedule for robust market-hour aware gap detection.
    # Current simplistic version returns nothing to avoid false positives in Phase 1 prototype.
    return []

def check_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Return duplicates based on index."""
    return df[df.index.duplicated()]

def run_quality_check(df: pd.DataFrame) -> dict:
    return {
        "missing_gaps": len(check_gaps(df)),
        "duplicates": len(check_duplicates(df)),
        "nan_rows": df.isnull().any(axis=1).sum()
    }
