import sys
import os
import argparse

# Ensure src is in path
sys.path.append(os.getcwd())

from src.utils.logger import configure_logger, get_logger
from src.utils.config import load_config
from src.brokers import ZerodhaBroker

configure_logger()
logger = get_logger("broker_test")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-margins", action="store_true")
    args = parser.parse_args()

    try:
        logger.info("init_broker", type="Zerodha")
        broker = ZerodhaBroker()
        
        # Test 1: Check Token presence
        if not broker.config.zerodha.access_token:
            logger.error("auth_failed", msg="No Access Token found in config/env. Cannot connect.")
            return

        # Test 2: Fetch Margins (Live Call)
        logger.info("fetching_margins")
        cash = broker.get_cash()
        logger.info("margin_check", available_cash=cash)
        
        if args.check_margins:
            # Maybe place a dummy order? No, user didn't ask for it yet.
            pass

        logger.info("connection_success", msg="Broker instantiated and API reachable.")

    except Exception as e:
        logger.exception("connection_failed", error=str(e))

if __name__ == "__main__":
    main()
