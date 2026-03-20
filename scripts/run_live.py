import sys
import os
import argparse
import signal
import time

# Ensure src is in path
sys.path.append(os.getcwd())

from src.live_trader import LiveTrader
from src.data.symbols import get_universe, Universe
from src.utils.logger import configure_logger, get_logger
from src.constants import Mode

configure_logger()
logger = get_logger("main")

def handle_exit(signum, frame):
    logger.info("shutdown_signal_received")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", type=str, default="NIFTY_NEXT50")
    parser.add_argument("--mode", type=str, default="LIVE", choices=["LIVE", "PAPER"])
    args = parser.parse_args()
    
    tickers = get_universe(Universe[args.universe])
    # tickers = tickers[:5] # Limit for testing?
    
    logger.info("starting_bot", universe=args.universe, count=len(tickers), mode=args.mode)
    
    mode_enum = Mode.LIVE if args.mode == "LIVE" else Mode.PAPER
    trader = LiveTrader(tickers=tickers, mode=mode_enum)
    trader.run_loop()

if __name__ == "__main__":
    main()
