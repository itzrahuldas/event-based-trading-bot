import sys
import os
import argparse

# Ensure src is in path
sys.path.append(os.getcwd())

from src.database import SessionLocal
from src.backtester import Backtester
from src.data.symbols import get_universe, Universe
from src.utils.logger import configure_logger

configure_logger()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=60)
    parser.add_argument("--universe", type=str, default="NIFTY_NEXT50")
    args = parser.parse_args()
    
    db = SessionLocal()
    tickers = get_universe(Universe[args.universe])
    
    # For rapid testing, if universe is large, maybe limit?
    # tickers = tickers[:5] 
    
    print(f"Starting Backtest on {args.universe} ({len(tickers)} tickers) for {args.days} days...")
    
    backtester = Backtester(db, tickers, days=args.days)
    backtester.run()
    
    db.close()

if __name__ == "__main__":
    main()
