from src.live_trader import LiveTrader
from src.data.symbols import get_universe
from src.constants import Universe, Mode
from src.utils.logger import get_logger, configure_logger

# Configure logging first
configure_logger()

logger = get_logger(__name__)

def main():
    logger.info("system_startup", msg="Starting Trading Bot...")
    
    # Load Universe
    tickers = get_universe(Universe.NIFTY_NEXT50)
    logger.info("universe_loaded", count=len(tickers))
    
    # Init Trader
    trader = LiveTrader(tickers=tickers, mode=Mode.PAPER)
    
    # Start Loop
    trader.run_loop()

if __name__ == "__main__":
    main()
