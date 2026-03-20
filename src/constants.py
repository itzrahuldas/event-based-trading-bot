from enum import Enum

class TimeFrame(str, Enum):
    M15 = "15m"
    H1 = "1h"
    D1 = "1d"

class Mode(str, Enum):
    LIVE = "LIVE"
    SIMULATION = "SIMULATION"
    BACKTEST = "BACKTEST"
    PAPER = "PAPER"

class Universe(str, Enum):
    NIFTY50 = "NIFTY50"
    NIFTY_NEXT50 = "NIFTY_NEXT50"
    NIFTY_MIDCAP = "NIFTY_MIDCAP"

# Defaults
DEFAULT_WARMUP_CANDLES = 200
DEFAULT_RISK_PER_TRADE = 0.01  # 1%
DEFAULT_MAX_TRADES_PER_DAY = 5
DEFAULT_SLIPPAGE_BPS = 5
DEFAULT_BROKERAGE_PER_TRADE = 20.0  # INR Flat
