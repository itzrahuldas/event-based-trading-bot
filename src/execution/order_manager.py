from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from src.constants import Mode
from src.domain_models import OrderRequest, OrderFill
from src.database import Trade
from src.brokers import Broker
from src.risk_manager import RiskManager
from src.run_manager import RunManager
from src.notify.notification_manager import NotificationManager, EventType
from src.notify.formatters import format_trade_fill, format_reject
from src.utils.logger import get_logger
from src.utils.time import now_utc

logger = get_logger(__name__)

class OrderManager:
    def __init__(self, db: Session, broker: Broker, risk_manager: RiskManager, run_manager: RunManager, notifier: NotificationManager, mode: Mode):
        self.db = db
        self.broker = broker
        self.risk_manager = risk_manager
        self.run_manager = run_manager
        self.notifier = notifier
        self.mode = mode

    def execute_signal(self, signal_data: Dict):
        """
        Orchestrates the execution of a signal:
        1. Extract Signal
        2. Risk Check
        3. Broker Order
        4. DB Persistence
        5. Notification
        """
        ticker = signal_data['ticker']
        signal = signal_data['signal']
        price = signal_data['price']
        atr = signal_data['atr']
        strategy = signal_data.get('strategy', 'MANUAL')
        
        logger.info("oms_signal_received", ticker=ticker, type=signal)
        
        if signal == "BUY":
            self._handle_buy(ticker, price, atr, strategy)
        elif signal == "SELL":
            self._handle_sell(ticker, price, strategy)

    def _handle_buy(self, ticker: str, price: float, atr: float, strategy: str):
        # [Idempotency Check]
        if self._check_if_already_traded(ticker, days=7):
            logger.info("oms_dedupe_skip", ticker=ticker, msg="Already bought in last 7 days")
            return

        if not self.risk_manager.can_trade():
            logger.warning("oms_risk_reject", ticker=ticker)
            return

        qty = self.risk_manager.calculate_quantity(price, atr)
        if qty <= 0:
            logger.warning("oms_qty_zero", ticker=ticker)
            return

        order = OrderRequest(ticker=ticker, side="BUY", quantity=qty)
        fill = self.broker.place_order(order)
        
        if fill:
            self._persist_trade(fill, strategy)
            self.notifier.send(EventType.TRADE_ENTRY, format_trade_fill(fill))
        else:
            self.notifier.send(EventType.ORDER_REJECTED, format_reject(order, "Execution Failed"))

    def _check_if_already_traded(self, ticker: str, days: int = 7) -> bool:
        """
        idempotency check: Returns True if we already bought this ticker recently.
        """
        from datetime import timedelta
        cutoff = now_utc() - timedelta(days=days)
        
        # Check DB for BUY trades for this ticker
        exists = self.db.query(Trade).filter(
            Trade.ticker == ticker,
            Trade.side == "BUY",
            Trade.timestamp >= cutoff
        ).first()
        
        return exists is not None

    def _handle_sell(self, ticker: str, price: float, strategy: str):
        # Determine quantity to close (Current Position)
        # Note: Broker.get_positions() might need to be refreshed or we rely on cache?
        # Ideally, we call get_positions() fresh.
        positions = self.broker.get_positions() # Helper to get fresh
        curr_state = positions.get(ticker)
        
        # If no position, nothing to sell
        if not curr_state or curr_state.quantity <= 0:
            return

        qty = curr_state.quantity
        order = OrderRequest(ticker=ticker, side="SELL", quantity=qty)
        fill = self.broker.place_order(order)
        
        if fill:
            self.risk_manager.update_metrics(fill.pnl)
            self._persist_trade(fill, strategy)
            self.notifier.send(EventType.TRADE_EXIT, format_trade_fill(fill))
        else:
            self.notifier.send(EventType.ORDER_REJECTED, format_reject(order, "Execution Failed"))

    def _persist_trade(self, fill: OrderFill, strategy: str):
        try:
            trade_record = Trade(
                timestamp=fill.timestamp or now_utc(),
                ticker=fill.ticker,
                side=fill.side,
                quantity=fill.quantity,
                price=fill.avg_price,
                pnl=fill.pnl if fill.pnl else 0.0,
                strategy=strategy,
                mode=self.mode,
                run_id=self.run_manager.get_run_id()
            )
            self.db.add(trade_record)
            self.db.commit()
            logger.info("oms_db_persisted", order_id=fill.order_id)
        except Exception as db_err:
            logger.error("oms_db_save_failed", error=str(db_err))
            self.db.rollback()
