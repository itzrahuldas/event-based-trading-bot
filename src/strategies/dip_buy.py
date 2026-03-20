import pandas as pd
from typing import Optional, Dict
from datetime import datetime
from src.domain_models import Signal
from src.strategies.base import Strategy
from src.constants import DEFAULT_WARMUP_CANDLES

class DipBuyStrategy(Strategy):
    def __init__(self):
        super().__init__(name="DipBuyStrategy", version="2.1")
        
    def generate_signal(self, ticker: str, df: pd.DataFrame) -> Optional[Signal]:
        """
        Trend Following Dip Buy Logic.
        Assumes df already has indicators: EMA_50, EMA_200, RSI, ATR, Vol_Avg
        """
        if len(df) < DEFAULT_WARMUP_CANDLES:
            return None
        
        # Analyze the LAST CLOSED candle
        curr = df.iloc[-1]
        
        # Check if indicators exist
        required_cols = ['EMA_50', 'EMA_200', 'RSI', 'ATR', 'Vol_Avg']
        for col in required_cols:
            if col not in curr or pd.isna(curr[col]):
                return None
        
        # Logic
        signals = {} # unused

        is_uptrend = curr['EMA_50'] > curr['EMA_200']
        is_oversold = curr['RSI'] < 35 
        vol_spike = curr['Volume'] > (1.2 * curr['Vol_Avg'])
        
        # BUY Logic
        if is_uptrend and is_oversold and vol_spike:
            return Signal(
                ticker=ticker,
                signal_type="BUY",
                price=curr['Close'],
                stop_loss=curr['ATR'], # Using ATR as SL proxy for now
                reason=f"DipBuy: RSI={curr['RSI']:.1f}, VolRatio={curr['Volume']/curr['Vol_Avg']:.1f}",
                generated_at=datetime.utcnow()
            )
            
        # SELL Logic (Exit)
        elif curr['RSI'] > 70:
             return Signal(
                ticker=ticker,
                signal_type="SELL",
                price=curr['Close'],
                stop_loss=0.0,
                reason=f"Exit: RSI={curr['RSI']:.1f}",
                generated_at=datetime.utcnow()
            )
            
        return None
