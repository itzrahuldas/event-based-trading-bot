from typing import Dict, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from src.database import Trade
from src.domain_models import OrderRequest, OrderFill, PositionState
from src.utils.config import load_config
from src.constants import Mode
from src.utils.logger import get_logger
from src.brokers.base import Broker

logger = get_logger(__name__)

class PaperBroker(Broker):
    def __init__(self, db: Optional[Session] = None, mode: Mode = Mode.PAPER, initial_cash: float = 100000.0, run_id: str = "sys"):
        self.cash = initial_cash
        self.positions: Dict[str, int] = {} # ticker -> qty
        self.avg_prices: Dict[str, float] = {} # ticker -> avg_buy_price
        self.config = load_config()
        self.db = db
        self.mode = mode
        self.run_id = run_id
        self._current_prices: Dict[str, float] = {} 

    def update_ltp(self, ticker: str, price: float):
        """Helper for Backtest/Sim to update 'Current Market Price'"""
        self._current_prices[ticker] = price

    def get_ltp(self, ticker: str) -> float:
        return self._current_prices.get(ticker, 0.0)

    def get_cash(self) -> float:
        return self.cash

    def get_orders(self) -> Any:
        return [] # TODO: Store order history in memory if needed for reconciliation test

    def get_positions(self) -> Dict[str, PositionState]:
        states = {}
        for ticker, qty in self.positions.items():
            if qty == 0: continue
            curr_price = self.get_ltp(ticker)
            avg_price = self.avg_prices.get(ticker, 0.0)
            pnl = (curr_price - avg_price) * qty if qty > 0 else 0 # Long only support for now
            
            states[ticker] = PositionState(
                ticker=ticker,
                quantity=qty,
                avg_price=avg_price,
                current_price=curr_price,
                pnl=pnl
            )
        return states

    def place_order(self, order: OrderRequest) -> Optional[OrderFill]:
        # Cost Logic
        ticker = order.ticker
        qty = order.quantity
        price = order.price if order.price else self.get_ltp(ticker)
        
        if price <= 0:
            logger.error("invalid_price", ticker=ticker, price=price)
            return None

        # Apply Slippage
        slippage_pct = self.config.backtest.slippage_bps / 10000.0
        pnl_realized = 0.0
        
        if order.side == "BUY":
            # Buy higher due to slippage
            exec_price = price * (1 + slippage_pct)
            total_cost = exec_price * qty + self.config.backtest.brokerage
            
            if self.cash < total_cost:
                logger.warning("insufficient_funds", cash=self.cash, cost=total_cost)
                return None
                
            # Update Position
            old_qty = self.positions.get(ticker, 0)
            old_avg = self.avg_prices.get(ticker, 0.0)
            
            if old_qty == 0:
                new_avg = exec_price
            else:
                new_avg = ((old_qty * old_avg) + (qty * exec_price)) / (old_qty + qty)
            
            self.positions[ticker] = old_qty + qty
            self.avg_prices[ticker] = new_avg
            self.cash -= total_cost
            
        elif order.side == "SELL":
            # Sell lower due to slippage
            exec_price = price * (1 - slippage_pct)
            total_proceeds = (exec_price * qty) - self.config.backtest.brokerage
            
            current_qty = self.positions.get(ticker, 0)
            if current_qty < qty:
                logger.warning("insufficient_shares", held=current_qty, ask=qty)
                return None
                
            # Realized PnL = (Exit - Entry) * Qty - Commission
            avg_price = self.avg_prices.get(ticker, 0.0)
            pnl_realized = (exec_price - avg_price) * qty - self.config.backtest.brokerage
            
            self.positions[ticker] -= qty
            self.cash += total_proceeds
            
            # Cleanup
            if self.positions[ticker] == 0:
                del self.avg_prices[ticker]
                del self.positions[ticker]
        else:
            return None

        fill = OrderFill(
            order_id=f"ord_{int(datetime.now().timestamp()*1000)}",
            ticker=ticker,
            side=order.side,
            quantity=qty,
            avg_price=exec_price,
            timestamp=datetime.now(),
            commission=self.config.backtest.brokerage,
            pnl=pnl_realized
        )
        
        logger.info("order_filled", fill=fill.model_dump())
        
        # PERSIST TO DB
        if self.db:
            try:
                t = Trade(
                    timestamp=fill.timestamp,
                    ticker=fill.ticker,
                    side=fill.side,
                    quantity=fill.quantity,
                    price=fill.avg_price,
                    pnl=fill.pnl,
                    reason="Signal",
                    mode=self.mode,
                    strategy_version="v2.0",
                    run_id=self.run_id
                )
                self.db.add(t)
                self.db.commit()
            except Exception as e:
                logger.error("db_persist_failed", error=str(e))
                self.db.rollback()

        return fill
    
    # PaperBroker doesn't strictly need normalize methods as it generates internal DTOs directly,
    # but we can implement them if we were simulating raw payloads.
    # For now, we leave them as inherited base methods (or pass if called).
