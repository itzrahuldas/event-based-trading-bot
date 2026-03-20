"""
Post-Market Report Generator

This script will:
1. Wait until Indian market close (3:30 PM IST)
2. Generate a comprehensive end-of-day trading report
3. Display results with trade summary and performance metrics
"""

import time
from datetime import datetime, time as dt_time
import pytz
from sqlalchemy import func, desc
from src.database import SessionLocal, Trade, RunLog
from src.ops.reporter import DailyReporter
from src.utils.time import now_utc, to_ist
from src.constants import Mode

def is_market_open():
    """Check if Indian market is currently open (9:15 AM - 3:30 PM IST)"""
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist).time()
    
    market_open = dt_time(9, 15)
    market_close = dt_time(15, 30)
    
    return market_open <= current_time <= market_close

def wait_until_market_close():
    """Wait until market closes at 3:30 PM IST"""
    ist = pytz.timezone('Asia/Kolkata')
    
    while is_market_open():
        current = datetime.now(ist)
        market_close = datetime.combine(current.date(), dt_time(15, 30))
        market_close = ist.localize(market_close)
        
        remaining = (market_close - current).total_seconds()
        
        if remaining > 0:
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            print(f"⏰ Market is open. Waiting for close... ({hours}h {minutes}m remaining)")
            
            # Check every 5 minutes during market hours
            time.sleep(300)
        else:
            break
    
    print("✅ Market has closed. Generating report...\n")

def generate_eod_report():
    """Generate end-of-day trading report"""
    db = SessionLocal()
    
    try:
        today = now_utc().date()
        
        # Get today's trades
        trades = db.query(Trade).filter(
            func.date(Trade.timestamp) == today,
            Trade.mode == Mode.LIVE
        ).order_by(Trade.timestamp).all()
        
        # Get today's run logs
        runs = db.query(RunLog).filter(
            func.date(RunLog.start_time) == today,
            RunLog.mode == Mode.LIVE
        ).order_by(desc(RunLog.start_time)).all()
        
        print("=" * 80)
        print(f"📊 END-OF-DAY TRADING REPORT - {today}")
        print("=" * 80)
        print()
        
        # System Status
        print("🤖 SYSTEM STATUS")
        print("-" * 80)
        print(f"Mode: LIVE")
        print(f"Report Date: {today}")
        print(f"Report Time: {to_ist(now_utc()).strftime('%Y-%m-%d %H:%M:%S IST')}")
        print(f"Total Runs Today: {len(runs)}")
        print()
        
        # Trading Activity
        print("📈 TRADING ACTIVITY")
        print("-" * 80)
        print(f"Total Trades Executed: {len(trades)}")
        
        if trades:
            # Calculate metrics
            gross_pnl = sum((t.pnl or 0) for t in trades)
            winners = [t for t in trades if (t.pnl or 0) > 0]
            losers = [t for t in trades if (t.pnl or 0) < 0]
            
            win_rate = (len(winners) / len(trades) * 100) if trades else 0
            
            avg_win = sum(t.pnl for t in winners) / len(winners) if winners else 0
            avg_loss = sum(t.pnl for t in losers) / len(losers) if losers else 0
            
            best_trade = max(trades, key=lambda t: (t.pnl or 0))
            worst_trade = min(trades, key=lambda t: (t.pnl or 0))
            
            print(f"Winners: {len(winners)}")
            print(f"Losers: {len(losers)}")
            print(f"Win Rate: {win_rate:.2f}%")
            print()
            
            # P&L Summary
            print("💰 P&L SUMMARY")
            print("-" * 80)
            print(f"Gross P&L: ₹{gross_pnl:,.2f}")
            print(f"Average Win: ₹{avg_win:,.2f}")
            print(f"Average Loss: ₹{avg_loss:,.2f}")
            print(f"Best Trade: {best_trade.ticker} (₹{best_trade.pnl:,.2f})")
            print(f"Worst Trade: {worst_trade.ticker} (₹{worst_trade.pnl:,.2f})")
            print()
            
            # Trade Details
            print("📋 TRADE DETAILS")
            print("-" * 80)
            print(f"{'Time':<12} {'Ticker':<15} {'Side':<6} {'Qty':<8} {'Price':<10} {'P&L':<12} {'Strategy':<15}")
            print("-" * 80)
            
            for trade in trades:
                trade_time = to_ist(trade.timestamp).strftime('%H:%M:%S')
                pnl_str = f"₹{trade.pnl:,.2f}" if trade.pnl else "N/A"
                
                print(f"{trade_time:<12} {trade.ticker:<15} {trade.side:<6} {trade.quantity:<8.0f} "
                      f"₹{trade.price:<9,.2f} {pnl_str:<12} {trade.strategy or 'N/A':<15}")
            
            print()
            
        else:
            print("No trades were executed today.")
            print()
        
        # Generate formal report using DailyReporter
        print("📄 GENERATING FORMAL REPORT...")
        print("-" * 80)
        
        reporter = DailyReporter()
        metrics = reporter.generate_report(
            report_date=today,
            universe="NIFTY_NEXT50",
            mode=Mode.LIVE,
            db=db
        )
        
        # Save to database
        reporter.save_report(
            metrics=metrics,
            mode=Mode.LIVE,
            universe="NIFTY_NEXT50",
            db=db
        )
        
        print("✅ Report saved to database")
        print()
        print("=" * 80)
        print("Report generation complete!")
        print("=" * 80)
        print()
        print("You can view the full report on the dashboard at: http://localhost:3000/reports")
        print()
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting Post-Market Report Generator")
    print()
    
    # Check if market is already closed
    if not is_market_open():
        print("ℹ️  Market is already closed. Generating report immediately...\n")
        generate_eod_report()
    else:
        # Wait for market close
        wait_until_market_close()
        generate_eod_report()
