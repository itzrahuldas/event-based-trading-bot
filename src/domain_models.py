from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
# Removed src.constants import to break cycle
# from src.constants import Mode (We will use str for now or explicit Enum if needed)

class Signal(BaseModel):
    ticker: str
    signal_type: str # BUY / SELL
    price: float
    stop_loss: float
    reason: str
    generated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class OrderRequest(BaseModel):
    ticker: str
    side: str # BUY / SELL
    quantity: int
    order_type: str = "MARKET"
    price: Optional[float] = None # For limit orders
    
class OrderFill(BaseModel):
    order_id: str
    ticker: str
    side: str
    quantity: int
    avg_price: float
    timestamp: datetime
    commission: float = 0.0
    pnl: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)

class PositionState(BaseModel):
    ticker: str
    quantity: int
    avg_price: float
    current_price: float
    pnl: float

class Trade(BaseModel):
    timestamp: datetime
    ticker: str
    side: str
    quantity: int
    price: float
    pnl: float
    strategy: str
    mode: str # Changed from Mode enum to str to avoid import cycle
    run_id: str
    reason: Optional[str] = "Signal"
    strategy_version: Optional[str] = "1.0"

    model_config = ConfigDict(from_attributes=True)

class RunStatus(BaseModel):
    run_id: str
    mode: str # Changed from Mode enum
    status: str
    error: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
