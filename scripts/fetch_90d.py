import sys
import os
import argparse

# Ensure src is in path
sys.path.append(os.getcwd())

from src.database import SessionLocal
from src.data.data_fetcher import DataFetcher
from src.data.symbols import get_universe, Universe

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=60, help="Days to fetch (max 60 for 15m usually)")
    parser.add_argument("--universe", type=str, default="NIFTY_NEXT50", help="NIFTY50 or NIFTY_NEXT50")
    args = parser.parse_args()
    
    db = SessionLocal()
    fetcher = DataFetcher(db)
    
    tickers = get_universe(Universe[args.universe])
    print(f"Fetching {args.days}d history for {len(tickers)} tickers in {args.universe}...")
    
    # New Batch Method
    summary = fetcher.fetch_batch_history(tickers, period=f"{args.days}d", interval="15m", max_workers=5)
    
    print("\n--- Summary ---")
    print(f"Total: {summary['total']}")
    print(f"Success: {summary['success']}")
    print(f"Failed: {summary['failed']}")
    if summary['failed'] > 0:
        print("Failures exist. Check logs.")
    print(f"\nCompleted! Total Records Added: {summary['total']}")
    db.close()

if __name__ == "__main__":
    main()
