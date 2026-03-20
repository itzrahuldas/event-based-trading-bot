from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session
from src.database import Price
from src.data.data_fetcher import DataFetcher
from src.strategies.indicators import calculate_indicators
from src.brokers import PaperBroker
from src.risk_manager import RiskManager
from src.portfolio_manager import PortfolioManager
from src.domain_models import OrderRequest
from src.utils.logger import get_logger
import structlog

from src.constants import Mode
import uuid

logger = get_logger(__name__)

class Backtester:
    def __init__(self, db: Session, universe: list, days: int = 60):
        self.db = db
        self.universe = universe
        self.days = days
        self.run_id = f"backtest_{str(uuid.uuid4())[:8]}"
        self.broker = PaperBroker(
            db=db, 
            mode=Mode.BACKTEST, 
            initial_cash=100000.0,
            run_id=self.run_id
        )
        self.risk_manager = RiskManager(broker=self.broker)
        self.fetcher = DataFetcher(db)
        self.portfolio_manager = PortfolioManager()
        
    def run(self):
        logger.info("backtest_start", universe_len=len(self.universe), days=self.days)
        
        # 1. Pre-load Data
        data_map = {}
        for ticker in self.universe:
            df = self.fetcher.get_prices(ticker, days=self.days)
            if not df.empty:
                df = calculate_indicators(df)
                data_map[ticker] = df
        
        if not data_map:
            logger.error("no_data_found")
            return
            
        # 2. Align Timestamps (Simulation Clock)
        # Find common start/end or just union all timestamps
        all_timestamps = sorted(list(set(ts for df in data_map.values() for ts in df.index)))
        
        # 3. Time Loop
        pending_orders = {} # ticker -> OrderRequest (Evaluated at Next Open)

        for current_ts in all_timestamps:
            # A. Execute Pending Orders (Market Open Simulation)
            for ticker, order in list(pending_orders.items()):
                df = data_map.get(ticker)
                if df is None: continue
                # Is there a candle at this timestamp?
                try:
                    row = df.loc[current_ts]
                    # Execute at OPEN price of this candle
                    order.price = row['Open']
                    # Update broker LTP for accurate position valuation
                    self.broker.update_ltp(ticker, row['Open']) 
                    
                    self.broker.place_order(order)
                    del pending_orders[ticker]
                except KeyError:
                    # No candle for this ticker at this time (gap?), delay execution
                    continue

            # B. Analyze & Generate Signals (End of Candle Simulation)
            for ticker in self.universe:
                df = data_map.get(ticker)
                if df is None: continue
                
                try:
                    # Update Broker LTP to Close for accurate valuation at EOD/EOC
                    row = df.loc[current_ts]
                    self.broker.update_ltp(ticker, row['Close'])
                    
                    # We need integer location for strategy analysis or pass the sliced DF
                    # PortfolioManager expects (ticker, df)
                    # To prevent future leak, we slice up to current_ts.
                    # Optimization: Passing full DF and index is faster, but PortfolioManager interface is (ticker, df).
                    # We will slice: data_upto_now = df.loc[:current_ts]
                    # This might be slow inside a loop. 
                    # V3.1 Optimization: pass index to Strategy.
                    
                    if current_ts not in df.index: continue
                    
                    # For performance, we can implement a "get_signal_at(index)" on Base Strategy?
                    # For now, safe and correct way: slice.
                    # Actually, if we pass full DF, the strategy usually inspects .iloc[-1].
                    # So we MUST pass a slice ending at current_ts.
                    
                    idx = df.index.get_loc(current_ts)
                    # Optimization check: minimal slice needed for indicators? 
                    # Indicators are already calc'd. We just need to hide future rows.
                    
                    curr_slice = df.iloc[:idx+1]
                    
                    signal_data = self.portfolio_manager.analyze(ticker, curr_slice)
                    
                    if signal_data:
                        signal = signal_data['signal']
                        price = signal_data['price'] # Close price
                        atr = signal_data['atr']
                        
                        # 1. Exit Logic (Sell)
                        if signal == "SELL":
                            qty = self.broker.positions.get(ticker, 0)
                            if qty > 0:
                                # Queue Sell for NEXT Open
                                pending_orders[ticker] = OrderRequest(
                                    ticker=ticker, side="SELL", quantity=qty # Sell All
                                )
                        
                        # 2. Entry Logic (Buy)
                        elif signal == "BUY":
                            # Check Risk
                            if self.risk_manager.can_trade():
                                qty = self.risk_manager.calculate_quantity(price, atr)
                                # Override usage of strategy weights?
                                # self.portfolio_manager.config... 
                                # For now, RiskManager handles generic sizing.
                                
                                if qty > 0:
                                    pending_orders[ticker] = OrderRequest(
                                        ticker=ticker, side="BUY", quantity=qty
                                    )
                                    
                except KeyError:
                    continue # No data for ticker at this timestamp
            
            # End of Time Step
            
        self.generate_report()

    def generate_report(self):
        final_value = self.broker.get_cash()
        positions = self.broker.get_positions()
        for ticker, pos in positions.items():
            final_value += (pos.quantity * pos.current_price)
            
        initial = 100000.0
        pnl = final_value - initial
        logger.info("backtest_complete", final_value=final_value, pnl=pnl, trades=len(self.broker.avg_prices)) # Approximation
        
        # print Summary
        print("\n" + "="*30)
        print("   BACKTEST REPORT")
        print("="*30)
        print(f"Initial Capital: {initial}")
        print(f"Final Value:     {final_value:.2f}")
        print(f"Net Profit:      {pnl:.2f} ({(pnl/initial)*100:.2f}%)")
        print("="*30)
