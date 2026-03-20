import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import SessionLocal, init_db
from src.backtester import Backtester
from src.data.symbols import get_universe, Universe

# Setup Logging
logging.basicConfig(level=logging.INFO)

def main():
    print("--- Running Backtest (Last 7 Days) ---")
    
    # 1. Init DB (Ensure tables exist)
    init_db()
    
    db = SessionLocal()
    
    # 2. Universe
    # 2. Universe
    # Comprehensive Universe: NIFTY50 + NEXT50
    u1 = get_universe(Universe.NIFTY50)
    u2 = get_universe(Universe.NIFTY_NEXT50)
    # u3 = get_universe(Universe.NIFTY_MIDCAP_100) # If available/supported
    
    tickers = list(set(u1 + u2))
    print(f"Universe: {len(tickers)} tickers (NIFTY50 + NEXT50)")
    
    # 3. Initialize Backtester
    # days=7 for last week
    bt = Backtester(db=db, universe=tickers, days=7)
    
    # 4. Run
    try:
        bt.run()
        print("\n[SUCCESS] Backtest completed.")
        print("Check Dashboard at http://localhost:3000 for results.")
    except Exception as e:
        print(f"[ERROR] Backtest Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
