import pandas as pd
from datetime import date, datetime
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from src.database import get_db, Trade, Report, SessionLocal
from src.utils.logger import get_logger
from src.notify.notification_manager import NotificationManager, EventType
from src.notify.formatters import format_daily_summary
import json

logger = get_logger(__name__)

class DailyReporter:
    def __init__(self):
        pass
        
    def generate_report(
        self, 
        report_date: date, 
        universe: str = "NIFTY_NEXT50", 
        mode: str = "LIVE", 
        db: Session = None
    ) -> dict:
        """
        Generates EOD report metrics.
        If db session provided, uses it. Otherwise opens new one.
        """
        logger.info("generating_report", date=report_date, mode=mode)
        
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
            
        try:
            # Fetch trades for the day
            # We filter by Trade.timestamp being on the same day
            trades = db.query(Trade).filter(
                func.date(Trade.timestamp) == report_date,
                Trade.mode == mode
            ).all()
            
            total_trades = len(trades)
            winners = [t for t in trades if ((t.pnl or 0) > 0)]
            losers = [t for t in trades if ((t.pnl or 0) < 0)]
            
            win_rate = (len(winners) / total_trades * 100) if total_trades > 0 else 0.0
            gross_pnl = sum((t.pnl or 0) for t in trades)
            
            # Simple simulation: assume pnl in DB is already Net or apply generic slippage if needed.
            # For now, keeping Gross = Net unless specific logic requested.
            net_pnl = gross_pnl 
            
            # Drawdown logic requires a running equity curve, which is hard with just EOD trades.
            # We can approximate max drawdown intraday if we strictly order trades.
            max_drawdown = 0.0
            if total_trades > 0:
                running_pnl = 0.0
                peak_pnl = 0.0
                min_pnl = 0.0
                
                # Sort by time
                sorted_trades = sorted(trades, key=lambda x: x.timestamp)
                for t in sorted_trades:
                    running_pnl += (t.pnl or 0)
                    if running_pnl > peak_pnl:
                        peak_pnl = running_pnl
                    dd = peak_pnl - running_pnl
                    if dd > max_drawdown:
                        max_drawdown = dd
            
            # Biggest Winner/Loser
            best_trade = max(trades, key=lambda t: (t.pnl or 0), default=None)
            worst_trade = min(trades, key=lambda t: (t.pnl or 0), default=None)
            
            metrics = {
                "date": str(report_date),
                "mode": mode,
                "universe": universe,
                "total_trades": total_trades,
                "win_rate": round(win_rate, 2),
                "gross_pnl": round(gross_pnl, 2),
                "net_pnl": round(net_pnl, 2),
                "max_drawdown": round(max_drawdown, 2),
                "best_ticker": best_trade.ticker if best_trade else None,
                "best_pnl": round(best_trade.pnl, 2) if best_trade else 0,
                "worst_ticker": worst_trade.ticker if worst_trade else None,
                "worst_pnl": round(worst_trade.pnl, 2) if worst_trade else 0,
            }
            
            return metrics
            
        finally:
            if close_db:
                db.close()

    def save_report(
        self, 
        metrics: dict, 
        mode: str = "LIVE",
        universe: str = "NIFTY_NEXT50",
        db: Session = None
    ):
        """Persist report to DB."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
            
        try:
            # Upsert logic
            report_date_str = metrics["date"]
            report_date = datetime.strptime(report_date_str, "%Y-%m-%d").date()
            
            # Check existing
            existing = db.query(Report).filter_by(
                report_date=report_date, 
                mode=mode, 
                universe=universe
            ).first()
            
            if existing:
                existing.metrics = metrics
                existing.created_at = datetime.now() # Update timestamp
                logger.info("updating_existing_report", id=existing.id)
            else:
                rpt = Report(
                    report_date=report_date,
                    mode=mode,
                    universe=universe,
                    metrics=metrics
                )
                db.add(rpt)
                logger.info("creating_new_report")
                
            db.commit()
            
        except Exception as e:
            logger.error("report_save_failed", error=str(e))
            db.rollback()
        finally:
            if close_db:
                db.close()

    def send_report(self, metrics: dict):
        """Mock sender + Telegram."""
        # ... logic unchanged ...
        from src.utils.config import load_config
        cfg = load_config()
        notifier = NotificationManager(cfg) 
        if notifier.enabled:
            msg = format_daily_summary(metrics)
            notifier.send(EventType.DAILY_SUMMARY, msg)
