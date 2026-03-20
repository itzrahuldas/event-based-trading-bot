from datetime import datetime
from src.utils.config import load_config
from src.brokers import Broker
import structlog

logger = structlog.get_logger()

class RiskManager:
    def __init__(self, broker: Broker):
        self.broker = broker
        self.config = load_config()
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.is_kill_switch_active = False
        
        # Drawdown Tracking
        self.peak_equity = 0.0
        self.is_halted_drawdown = False

    def can_trade(self) -> bool:
        """Check Kill-Switch, Drawdown Halt, and Max Trades."""
        if self.is_kill_switch_active:
            logger.error("kill_switch_active", msg="Trading Halted due to Daily Loss Limit.")
            return False
            
        if self.is_halted_drawdown:
            logger.error("drawdown_halt_active", msg="Trading Halted due to Max Drawdown Breach.")
            return False

        if self.daily_trades >= self.config.risk.max_trades_per_day:
            logger.warning("max_daily_trades_reached", limit=self.config.risk.max_trades_per_day)
            return False
            
        return True

    def calculate_quantity(self, price: float, atr: float) -> int:
        """Calculate Position Size based on Risk per Trade."""
        if not self.can_trade(): return 0
        
        cash = self.broker.get_cash()
        risk_amt = cash * self.config.risk.risk_per_trade
        
        if atr <= 0:
            logger.error("invalid_atr", atr=atr)
            return 0
            
        sl_distance = 2 * atr
        raw_qty = risk_amt / sl_distance
        
        qty = int(raw_qty)
        
        # Sanity check
        cost = qty * price
        if cost > cash:
            qty = int(cash / price)
        
        return max(0, qty)

    def update_metrics(self, pnl: float):
        """Update metrics after a trade close."""
        self.daily_pnl += pnl
        self.daily_trades += 1
        
        # Check Daily Loss Limit
        if self.daily_pnl <= -self.config.risk.max_daily_loss:
            self.is_kill_switch_active = True
            logger.critical("kill_switch_TRIGGERED", daily_pnl=self.daily_pnl, limit=self.config.risk.max_daily_loss)

        # Check Max Drawdown Logic
        current_equity = self.broker.get_cash() # Assuming cash is mostly equity for now (ignoring open positions pnl for safe check)
        
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
            
        if self.peak_equity > 0:
            drawdown_pct = (self.peak_equity - current_equity) / self.peak_equity
            # Example: 5% Max Drawdown Config
            MAX_DD = 0.05 
            if drawdown_pct >= MAX_DD:
                self.is_halted_drawdown = True
                logger.critical("max_drawdown_TRIGGERED", drawdown_pct=drawdown_pct, limit=MAX_DD)
