from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.constants import Mode

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

class RunStatus(BaseModel):
    run_id: str
    mode: Mode
    status: str
    error: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
