import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import func

# Add project root to path
sys.path.append(os.getcwd())

from src.database import SessionLocal, Trade
from src.utils.logger import configure_logger
import structlog

configure_logger()
logger = structlog.get_logger()

def generate_weekly_report(mode="PAPER"):
    db = SessionLocal()
    with open("weekly_report.txt", "w", encoding="utf-8") as f:
        try:
            today = datetime.utcnow().date()
            start_of_week = today - timedelta(days=today.weekday()) # Monday
            
            f.write(f"Generating Weekly Report ({mode})\n")
            f.write(f"Period: {start_of_week} to {today}\n\n")
            
            # Debug: Check all trades
            all_trades = db.query(Trade).all()
            f.write(f"DEBUG: Total trades in DB: {len(all_trades)}\n")
            if all_trades:
                t = all_trades[0]
                f.write(f"DEBUG: First ID: {t.id}\n")
                f.write(f"DEBUG: Timestamp: {t.timestamp} (Type: {type(t.timestamp)})\n")
                f.write(f"DEBUG: Mode: '{t.mode}' (Type: {type(t.mode)})\n")
            
            trades = db.query(Trade).filter(
                Trade.timestamp >= start_of_week
            ).all()

            # Filter by mode in python to be safe if DB has issues
            # Relaxed filter: matches if mode matches or if mode is None in DB
            filtered_trades = [t for t in trades if str(t.mode) == mode or t.mode is None]
            
            if not filtered_trades:
                f.write("No trades found for this week (after filtering).\n")
                return

            total_trades = len(filtered_trades)
            winners = [t for t in filtered_trades if ((t.pnl or 0) > 0)]
            losers = [t for t in filtered_trades if ((t.pnl or 0) < 0)]
            
            win_rate = (len(winners) / total_trades * 100) if total_trades > 0 else 0.0
            gross_pnl = sum((t.pnl or 0) for t in filtered_trades)
            net_pnl = gross_pnl 
            
            # Best/Worst
            best_trade = max(filtered_trades, key=lambda t: (t.pnl or 0), default=None)
            worst_trade = min(filtered_trades, key=lambda t: (t.pnl or 0), default=None)

            f.write("-" * 40 + "\n")
            f.write(f"Total Trades: {total_trades}\n")
            f.write(f"Win Rate:     {win_rate:.2f}%\n")
            f.write(f"Gross PnL:    Rs {gross_pnl:.2f}\n")
            f.write(f"Net PnL:      Rs {net_pnl:.2f}\n")
            f.write("-" * 40 + "\n")
            if best_trade:
                f.write(f"Best Trade:   {best_trade.ticker} (Rs {best_trade.pnl:.2f})\n")
            if worst_trade:
                f.write(f"Worst Trade:  {worst_trade.ticker} (Rs {worst_trade.pnl:.2f})\n")
            f.write("-" * 40 + "\n")
            
            # Detailed List
            f.write("\nTrade Log:\n")
            f.write(f"{'Time':<20} {'Ticker':<10} {'Side':<5} {'Qty':<5} {'Price':<10} {'PnL':<10}\n")
            for t in sorted(filtered_trades, key=lambda x: x.timestamp):
                pnl = t.pnl if t.pnl is not None else 0.0
                f.write(f"{str(t.timestamp)[:19]:<20} {t.ticker:<10} {t.side:<5} {t.quantity:<5} {t.price:<10.2f} {pnl:<10.2f}\n")

        except Exception as e:
            logger.exception("weekly_report_failed")
            f.write(f"Error: {e}\n")
        finally:
            db.close()

if __name__ == "__main__":
    generate_weekly_report(mode="LIVE")
    # Also append/check PAPER if needed, but file overwrite mode "w" prevents appending.
    # Let's just run LIVE as that's where the data is.
