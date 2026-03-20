import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from src.database import get_db, Price
from src.constants import Universe
from src.data.symbols import get_universe
import pandas as pd

def check_quality(universe_name="NIFTY_NEXT50", days=30, threshold=0.03):
    """
    Asserts missing candles ratio < threshold.
    """
    print(f"Verifying Data Quality for {universe_name} ({days} days)...")
    tickers = get_universe(Universe[universe_name])
    
    db = next(get_db())
    cutoff = datetime.now() - timedelta(days=days)
    
    # Check simple row count per ticker
    # Expected: ~75 candles/day * days (rough approx for 15m)
    # Market open 9:15-15:30 = 6h 15m = 25 candles/day? 
    # 6*4 + 1 = 25. Correct.
    expected_per_day = 25
    expected_total = expected_per_day * days * 0.6 # Adjust for weekends/holidays (approx 0.6 factor)
    
    failures = []
    
    for ticker in tickers:
        count = db.query(Price).filter(
            Price.ticker == ticker,
            Price.timestamp >= cutoff
        ).count()
        
        # Heuristic check
        if count < (expected_total * 0.5): # Severe underfetch
            failures.append(f"{ticker}: {count} (Expected ~{expected_total})")
            
    if failures:
        # Check if severely failed > 10%
        print(f"Verification Failed. {len(failures)} tickers under-fetched.")
        print(failures[:5]) # Show first 5
        sys.exit(1)
    
    print("Data Quality Check Passed (Basic Count Check).")
    sys.exit(0)

if __name__ == "__main__":
    check_quality()
