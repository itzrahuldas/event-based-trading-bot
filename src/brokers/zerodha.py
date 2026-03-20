from typing import Dict, Optional, Any
from datetime import datetime
try:
    import kiteconnect
except ImportError:
    kiteconnect = None

from src.brokers.base import Broker
from src.domain_models import OrderRequest, OrderFill, PositionState
from src.utils.config import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ZerodhaBroker(Broker):
    def __init__(self):
        self.config = load_config()
        self.kite = kiteconnect.KiteConnect(api_key=self.config.zerodha.api_key)
        
        # In a real scenario, we need an access_token.
        # This is usually generated via a login flow (Get Request Token -> Post for Access Token).
        # For this implementation, we assume access_token is already provided in env/config (Manual or Auto-login script).
        if hasattr(self.config.zerodha, 'access_token') and self.config.zerodha.access_token:
            self.kite.set_access_token(self.config.zerodha.access_token)
        else:
            logger.warning("zerodha_no_token", msg="Access Token missing. Initialize manually.")
            
        self.positions = {}

    def get_ltp(self, ticker: str) -> float:
        """
        Get LTP for NSE ticker.
        Ticker format: 'RELIANCE.NS' -> 'NSE:RELIANCE'
        """
        # Convert YFinance/Internal ticker to Zerodha format
        z_ticker = f"NSE:{ticker.replace('.NS', '')}"
        try:
            quote = self.kite.ltp(z_ticker)
            return quote[z_ticker]['last_price']
        except Exception as e:
            logger.error("zerodha_ltp_failed", ticker=ticker, error=str(e))
            return 0.0

    def place_order(self, order: OrderRequest) -> Optional[OrderFill]:
        """
        Place order on Zerodha.
        """
        tradingsymbol = order.ticker.replace('.NS', '')
        exchange = "NSE"
        transaction_type = self.kite.TRANSACTION_TYPE_BUY if order.side == "BUY" else self.kite.TRANSACTION_TYPE_SELL
        quantity = int(order.quantity)
        order_type = self.kite.ORDER_TYPE_MARKET
        product = self.kite.PRODUCT_MIS # Intraday
        
        try:
            order_id = self.kite.place_order(
                tradingsymbol=tradingsymbol,
                exchange=exchange,
                transaction_type=transaction_type,
                quantity=quantity,
                variety=self.kite.VARIETY_REGULAR,
                order_type=order_type,
                product=product,
                validity=self.kite.VALIDITY_DAY
            )
            
            logger.info("zerodha_order_placed", order_id=order_id, ticker=order.ticker)
            
            # Zerodha returns just Order ID immediately.
            # We must fetch order details to get fill price.
            # Ideally, we wait for a callback or poll order status.
            # For simplicity: We return a provisional fill with approximate price (LTP).
            # The Calibration Job will update it later.
            
            # OR we fetch order book immediately (might have lag)
            # order_details = self.kite.order_history(order_id)[-1]
            
            # Using normalize_order pattern on a basic dict construction for now
            return OrderFill(
                order_id=str(order_id),
                ticker=order.ticker,
                side=order.side,
                quantity=quantity,
                avg_price=0.0, # Unknown at placement, will be updated by tradebook
                timestamp=datetime.now(),
                commission=0.0, # Zerodha specific
                pnl=0.0
            )
            
        except Exception as e:
            logger.error("zerodha_order_failed", ticker=order.ticker, error=str(e))
            return None

    def get_positions(self) -> Dict[str, PositionState]:
        """Fetch Net Positions."""
        try:
            response = self.kite.positions()
            net_positions = response.get('net', [])
            self.positions = self.normalize_positions(net_positions)
            return self.positions
        except Exception as e:
            logger.error("zerodha_positions_failed", error=str(e))
            return {}

    def get_cash(self) -> float:
        try:
            margins = self.kite.margins()
            return margins['equity']['net']
        except Exception as e:
            logger.error("zerodha_margin_failed", error=str(e))
            return 0.0

    def get_orders(self) -> Any:
        try:
            return self.kite.orders()
        except Exception as e:
            logger.error("zerodha_orders_failed", error=str(e))
            return []

    # --- Adapter Implementations ---

    def normalize_positions(self, data: Any) -> Dict[str, PositionState]:
        states = {}
        for p in data:
            # Zerodha keys: tradingsymbol, exchange, quantity, average_price, last_price, pnl
            ticker = f"{p['tradingsymbol']}.NS" if p['exchange'] == 'NSE' else p['tradingsymbol']
            
            states[ticker] = PositionState(
                ticker=ticker,
                quantity=int(p['quantity']),
                avg_price=float(p['average_price']),
                current_price=float(p['last_price']),
                pnl=float(p['pnl'])
            )
        return states

    def normalize_order(self, data: Any) -> OrderFill:
        # Implementation depends on the API response structure passed
        pass
