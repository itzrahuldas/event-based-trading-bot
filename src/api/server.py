from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict
from datetime import datetime
import json
import asyncio
import pytz
from pydantic import BaseModel

from src.database import get_db, RunLog, Trade, Report, Price, SessionLocal
from src.utils.logger import get_logger
from src.utils.time import now_utc, to_ist

logger = get_logger(__name__)

app = FastAPI(title="Event-Based Trading Bot API", version="4.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for Response ---
class RunLogDTO(BaseModel):
    run_id: str
    mode: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    end_reason: Optional[str] = None
    
    class Config:
        from_attributes = True

class TradeDTO(BaseModel):
    id: int
    timestamp: datetime
    ticker: str
    side: str
    quantity: float
    price: float
    pnl: Optional[float] = None
    strategy: Optional[str] = None
    
    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    status: str
    mode: str
    timestamp: datetime
    db_ok: bool

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# --- Endpoints ---

@app.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    try:
        # Simple DB check
        db.execute(func.now()) 
        db_ok = True
    except Exception as e:
        logger.error("api_health_db_fail", error=str(e))
        db_ok = False
        
    return {
        "status": "online",
        "mode": "API",
        "timestamp": now_utc(),
        "db_ok": db_ok
    }

@app.get("/runs", response_model=List[RunLogDTO])
def get_runs(limit: int = 50, db: Session = Depends(get_db)):
    runs = db.query(RunLog).order_by(desc(RunLog.start_time)).limit(limit).all()
    return runs

@app.get("/trades", response_model=List[TradeDTO])
def get_trades(limit: int = 200, db: Session = Depends(get_db)):
    trades = db.query(Trade).order_by(desc(Trade.timestamp)).limit(limit).all()
    return trades

from src.ops.reporter import DailyReporter

# ... imports ...

@app.get("/reports/latest")
def get_latest_report(mode: str = "PAPER", universe: str = "NIFTY_NEXT50", db: Session = Depends(get_db)):
    """
    Get latest report.
    Logic:
    1. Check if trades exist for TODAY. If yes, generate/return TODAY's report.
    2. If no trades TODAY, find the DATE of the MOST RECENT trade (for this mode).
    3. Generate/Return report for THAT date.
    4. If no trades ever, return Today's empty report.
    """
    today = now_utc().date()
    
    # Check for trades today
    trades_today_count = db.query(Trade).filter(
        func.date(Trade.timestamp) == today, 
        Trade.mode == mode
    ).count()
    
    target_date = today
    
    if trades_today_count == 0:
        # Find last trade date
        last_trade = db.query(Trade).filter(Trade.mode == mode).order_by(desc(Trade.timestamp)).first()
        if last_trade:
            # Use that date
            # Ensure we handle naive/aware timestamp correctly
            ts = last_trade.timestamp
            # If ts is datetime, get date.
            target_date = ts.date()
            
    # Now get/gen report for target_date
    r = db.query(Report).filter(
        Report.report_date == target_date, 
        Report.mode == mode,
        Report.universe == universe
    ).first()
    
    metrics = None
    if r:
         metrics = r.metrics
         if isinstance(metrics, str):
            try:
                metrics = json.loads(metrics)
            except:
                pass
    else:
        # Generate on fly
        reporter = DailyReporter()
        metrics = reporter.generate_report(report_date=target_date, universe=universe, mode=mode, db=db)
        
    return {
        "date": str(target_date),
        "mode": mode,
        "metrics": metrics
    }

class GenerateReportRequest(BaseModel):
    date: str # YYYY-MM-DD
    mode: str
    universe: str = "NIFTY_NEXT50"

@app.post("/reports/generate")
def generate_report_endpoint(req: GenerateReportRequest, db: Session = Depends(get_db)):
    try:
        target_date = datetime.strptime(req.date, "%Y-%m-%d").date()
        reporter = DailyReporter()
        
        # Generate
        metrics = reporter.generate_report(
            report_date=target_date, 
            universe=req.universe, 
            mode=req.mode, 
            db=db
        )
        
        # Save
        reporter.save_report(
            metrics=metrics, 
            mode=req.mode, 
            universe=req.universe, 
            db=db
        )
        
        return {
            "status": "success",
            "date": str(target_date),
            "mode": req.mode,
            "metrics": metrics
        }
    except Exception as e:
        logger.error("api_gen_report_fail", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prices/latest")
def get_latest_prices(universe: str = "NIFTY_NEXT50", interval: str = "15m", db: Session = Depends(get_db)):
    # Complex query to get max timestamp per ticker?
    # For prototype, just list last 100 prices sorted by time desc to see freshness
    # or specific logic if needed.
    # Group by logic is slow on SQLite sometimes.
    # Just return last 50 prices overall
    prices = db.query(Price).order_by(desc(Price.timestamp)).limit(50).all()
    result = []
    for p in prices:
        # Handle naive datetimes from database
        timestamp = p.timestamp
        if timestamp.tzinfo is None:
            # Assume UTC if naive
            timestamp = timestamp.replace(tzinfo=pytz.UTC)
        result.append({
            "ticker": p.ticker, 
            "time": to_ist(timestamp).strftime("%Y-%m-%d %H:%M:%S"), 
            "close": p.close
        })
    return result

# --- WebSocket Stream ---
@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Heartbeat / basic polling loop simulation
            # In a real event system, we'd hook into an event bus.
            # Here we just push time every 5s
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("ws_error", error=str(e))
        try:
            manager.disconnect(websocket)
        except:
             pass
# --- Webhook for Broadcast ---
class WebhookNotifyRequest(BaseModel):
    type: str # e.g. TRADE_ENTRY, TRADE_EXIT
    data: dict

@app.post("/webhook/notify")
async def notify_webhook(req: WebhookNotifyRequest):
    """
    Internal endpoint for workers to push events to frontend via WS.
    """
    payload = {
        "type": req.type,
        "data": req.data,
        "timestamp": str(now_utc())
    }
    await manager.broadcast(payload)
    return {"status": "broadcasted"}

@app.get("/reports/weekly")
def get_weekly_report(mode: str = "PAPER", universe: str = "NIFTY_NEXT50", db: Session = Depends(get_db)):
    """
    Get weekly report (Monday to Today).
    """
    try:
        from datetime import timedelta
        
        today = now_utc().date()
        start_of_week = today - timedelta(days=today.weekday()) # Monday
        
        # 1. Fetch trades
        # Depending on how 'mode' is stored (enum vs str), cast or filter normally
        # In script we saw filtering needed care.
        trades = db.query(Trade).filter(
            Trade.timestamp >= start_of_week,
            Trade.mode == mode
        ).all()
        
        # 2. Calculate Metrics
        total_trades = len(trades)
        winners = [t for t in trades if ((t.pnl or 0) > 0)]
        gross_pnl = sum((t.pnl or 0) for t in trades)
        net_pnl = gross_pnl 
        win_rate = (len(winners) / total_trades * 100) if total_trades > 0 else 0.0
        
        # Drawdown logic (Approx for entire week based on sequence)
        max_drawdown = 0.0
        if total_trades > 0:
            running_pnl = 0.0
            peak_pnl = 0.0
            sorted_trades = sorted(trades, key=lambda x: x.timestamp)
            for t in sorted_trades:
                running_pnl += (t.pnl or 0)
                if running_pnl > peak_pnl:
                    peak_pnl = running_pnl
                dd = peak_pnl - running_pnl
                if dd > max_drawdown:
                    max_drawdown = dd
        
        best_trade = max(trades, key=lambda t: (t.pnl or 0), default=None)
        worst_trade = min(trades, key=lambda t: (t.pnl or 0), default=None)
        
        metrics = {
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
        
        return {
            "date": f"{start_of_week} to {today}",
            "mode": mode,
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error("api_weekly_report_fail", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
