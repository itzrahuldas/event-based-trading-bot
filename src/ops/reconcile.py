from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database import SessionLocal, Trade
from src.brokers import ZerodhaBroker
from src.utils.logger import configure_logger, get_logger
from src.utils.config import load_config
import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

configure_logger()
logger = get_logger("reconciler")

def reconcile_trades(db: Session, broker):
    """
    Compare DB Trades vs Broker Orders for today.
    """
    today = datetime.utcnow().date()
    
    # 1. Fetch DB Trades
    db_trades = db.query(Trade).filter(
        Trade.timestamp >= today
    ).all()
    
    # 2. Fetch Broker Orders
    # Filter for Completed/Filled orders only
    broker_orders = broker.get_orders()
    filled_orders = [o for o in broker_orders if o['status'] == 'COMPLETE']
    
    logger.info("reconciliation_start", db_count=len(db_trades), broker_count=len(filled_orders))
    
    # Logic:
    # Key = Ticker + Side (Simple aggregation check for now)
    # Or strict OrderID matching if we store Broker Order ID in DB.
    # Currently DB stores generated "ord_..." ID. 
    # If we are live trading, we should store Zerodha's Order ID.
    # v3.0 TODO: Update DB Schema to split 'internal_order_id' and 'broker_order_id'.
    # For now, we do a quantity sum check per ticker.
    
    db_summary = {}
    for t in db_trades:
        key = (t.ticker, t.side)
        db_summary[key] = db_summary.get(key, 0) + t.quantity

    broker_summary = {}
    for o in filled_orders:
        # Zerodha ticker is 'INFY', DB is 'INFY.NS'. Normalize.
        ticker = f"{o['tradingsymbol']}.NS" if 'NSE' in o.get('exchange', 'NSE') else o['tradingsymbol']
        side = "BUY" if o['transaction_type'] == 'BUY' else "SELL"
        key = (ticker, side)
        broker_summary[key] = broker_summary.get(key, 0) + int(o['quantity'])
        
    # Compare
    all_keys = set(db_summary.keys()) | set(broker_summary.keys())
    mismatches = []
    
    for key in all_keys:
        db_qty = db_summary.get(key, 0)
        bk_qty = broker_summary.get(key, 0)
        
        if db_qty != bk_qty:
            mismatches.append({
                "ticker": key[0],
                "side": key[1],
                "db_qty": db_qty,
                "broker_qty": bk_qty,
                "diff": db_qty - bk_qty
            })
            
    if mismatches:
        logger.error("reconciliation_mismatches_found", count=len(mismatches))
        for m in mismatches:
            logger.error("mismatch", **m)
    else:
        logger.info("reconciliation_success", msg="DB and Broker are in sync.")

def main():
    # Only run if configured for Real Trading
    # Or enforce explicit flag
    config = load_config()
    
    # We instantiate ZerodhaBroker to check status
    # If using PaperBroker, get_orders returns [], so it reconciles if DB is empty.
    
    # Ideally, pass the broker instance used in LiveTrader.
    # Here we create a fresh one.
    try:
        broker = ZerodhaBroker() 
        # Check connection implicitly via init
    except Exception as e:
        logger.error("broker_init_failed", error=str(e))
        return

    db = SessionLocal()
    try:
        reconcile_trades(db, broker)
    finally:
        db.close()

if __name__ == "__main__":
    main()
