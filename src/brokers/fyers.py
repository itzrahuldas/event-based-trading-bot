from typing import Dict, Optional, Any
from datetime import datetime
try:
    from fyers_apiv3 import fyersModel
except ImportError:
    fyersModel = None

from src.brokers.base import Broker
from src.domain_models import OrderRequest, OrderFill, PositionState
from src.utils.config import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class FyersBroker(Broker):
    def __init__(self):
        self.config = load_config()
        self.fyers = None
        
        # Check for dependencies
        if fyersModel is None:
            logger.error("fyers_lib_missing", msg="Install fyers-apiv3 to use FyersBroker")
            return
            
        self.client_id = self.config.fyers.client_id
        self.secret_key = self.config.fyers.secret_key
        self.access_token = self.config.fyers.access_token
        
        if self.access_token:
            self._initialize_session()
        else:
            logger.warning("fyers_no_token", msg="Access Token missing. Initialize manually or use auto-login.")

    def _initialize_session(self):
        try:
            self.fyers = fyersModel.FyersModel(
                client_id=self.client_id, 
                token=self.access_token,
                is_async=False, 
                log_path=""
            )
            # Verify?
            # self.fyers.get_profile()
        except Exception as e:
            logger.error("fyers_init_failed", error=str(e))

    def get_ltp(self, ticker: str) -> float:
        """
        Get LTP for NSE ticker.
        Ticker format: 'RELIANCE.NS' -> 'NSE:RELIANCE-EQ' (Fyers format usually Exchange:Symbol-Series)
        Common Fyers Format: 'NSE:RELIANCE-EQ' or 'NSE:NIFTY50-INDEX'
        """
        # Simple heuristic mapping
        symbol = ticker.replace('.NS', '')
        # For Equity, Fyers uses -EQ suffix often or just symbol?
        # Let's assume input 'NSE:RELIANCE-EQ' style or construct it.
        # User input is typically 'RELIANCE.NS' -> 'NSE:RELIANCE-EQ'
        
        fyers_symbol = f"NSE:{symbol}-EQ"
        if symbol in ["NIFTY 50", "NIFTY BANK"]: # Indices are special
             fyers_symbol = f"NSE:{symbol.replace(' ', '')}-INDEX"
             
        data = {
            "symbols": fyers_symbol
        }
        
        try:
            response = self.fyers.quotes(data=data)
            # Response: {'s': 'ok', 'd': [{'n': 'NSE:RELIANCE-EQ', 's': 'ok', 'v': {'lp': 2500.0, ...}}]}
            if response.get('s') == 'ok' and response.get('d'):
                return response['d'][0]['v']['lp']
            return 0.0
        except Exception as e:
            logger.error("fyers_ltp_failed", ticker=ticker, error=str(e))
            return 0.0

    def place_order(self, order: OrderRequest) -> Optional[OrderFill]:
        """
        Place order on Fyers.
        """
        symbol = order.ticker.replace('.NS', '')
        fyers_symbol = f"NSE:{symbol}-EQ" # Assuming Equity
        
        # Map Constants
        # Side: 1 (Buy), -1 (Sell)
        side = 1 if order.side == "BUY" else -1
        
        # Type: 1 (Limit), 2 (Market)
        type_map = {
            "LIMIT": 1,
            "MARKET": 2,
            "SL": 3,
            "SL-M": 4
        }
        order_type = type_map.get(order.order_type, 2)
        
        # Product: Intraday='INTRADAY', CNC='CNC', CO='CO'
        product = "INTRADAY" 
        
        data = {
            "symbol": fyers_symbol,
            "qty": int(order.quantity),
            "type": order_type,
            "side": side,
            "productType": product,
            "limitPrice": float(order.price) if order.price else 0,
            "stopPrice": 0, # Add if needed
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": False,
        }
        
        try:
            response = self.fyers.place_order(data=data)
            # Response: {'s': 'ok', 'code': 1101, 'message': 'Order submitted', 'id': '12345'}
            
            if response.get('s') == 'ok':
                order_id = response.get('id')
                logger.info("fyers_order_placed", order_id=order_id, ticker=order.ticker)
                
                return OrderFill(
                    order_id=str(order_id),
                    ticker=order.ticker,
                    side=order.side,
                    quantity=int(order.quantity),
                    avg_price=0.0, # Unknown at placement
                    timestamp=datetime.now(),
                    commission=0.0,
                    pnl=0.0
                )
            else:
                 logger.error("fyers_order_rejected", msg=response.get('message'))
                 return None
                 
        except Exception as e:
            logger.error("fyers_order_failed", ticker=order.ticker, error=str(e))
            return None

    def get_positions(self) -> Dict[str, PositionState]:
        try:
            response = self.fyers.positions()
            # Fyers Response: {'s': 'ok', 'netPositions': [...]}
            if response.get('s') != 'ok':
                 return {}
                 
            net_positions = response.get('netPositions', [])
            return self.normalize_positions(net_positions)
        except Exception as e:
            logger.error("fyers_positions_failed", error=str(e))
            return {}

    def get_cash(self) -> float:
        try:
            response = self.fyers.funds()
            # {'s': 'ok', 'fund_limit': [{'id': 10, 'title': 'Total Balance', 'equityAmount': 50000.0, ...}]}
            if response.get('s') == 'ok':
                funds = response.get('fund_limit', [])
                for fund in funds:
                    if fund.get('title') == 'Available Balance' or fund.get('id') == 10: # Check logic
                        return float(fund.get('equityAmount', 0.0))
            return 0.0
        except Exception as e:
            logger.error("fyers_funds_failed", error=str(e))
            return 0.0

    def get_orders(self) -> Any:
        try:
             return self.fyers.orderbook()
        except:
             return []

    # --- Adapter Implementations ---

    def normalize_positions(self, data: Any) -> Dict[str, PositionState]:
        states = {}
        for p in data:
            # Fyers keys: symbol, netQty, avgPrice, ltp, pl
            # symbol: 'NSE:SBIN-EQ'
            raw_sym = p.get('symbol', '')
            # Convert back to internal: 'SBIN' + '.NS' if NSE
            ticker = raw_sym # Raw for now or parse
            if raw_sym.startswith('NSE:'):
                part = raw_sym.replace('NSE:', '').replace('-EQ', '')
                ticker = f"{part}.NS"
            
            states[ticker] = PositionState(
                ticker=ticker,
                quantity=int(p.get('netQty', 0)),
                avg_price=float(p.get('avgPrice', 0.0)),
                current_price=float(p.get('ltp', 0.0)),
                pnl=float(p.get('pl', 0.0))
            )
        return states
