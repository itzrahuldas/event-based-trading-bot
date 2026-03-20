from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from src.domain_models import OrderRequest, OrderFill, PositionState
from src.utils.logger import get_logger

logger = get_logger(__name__)

class Broker(ABC):
    """
    Abstract Base Class for all Brokers (Paper, Zerodha, Angel, etc.)
    Enforces the Adapter Pattern to normalize data across different APIs.
    """
    
    @abstractmethod
    def get_ltp(self, ticker: str) -> float:
        """Get Last Traded Price for a single ticker."""
        pass
        
    @abstractmethod
    def place_order(self, order: OrderRequest) -> Optional[OrderFill]:
        """Place an order and return the normalized fill details."""
        pass
        
    @abstractmethod
    def get_positions(self) -> Dict[str, PositionState]:
        """Get current open positions normalized to PositionState."""
        pass
        
    @abstractmethod
    def get_cash(self) -> float:
        """Get available cash/margin."""
        pass

    @abstractmethod
    def get_orders(self) -> Any:
        """Get all orders for the current day."""
        pass

    # --- Adapter Contract: Normalization Methods ---
    
    def normalize_order(self, data: Any) -> OrderFill:
        """
        Convert broker-specific order response to OrderFill DTO.
        Must be implemented by subclasses if they handle raw payloads.
        """
        raise NotImplementedError("Subclasses must implement normalize_order")

    def normalize_position(self, data: Any) -> PositionState:
        """
        Convert broker-specific position payload to PositionState DTO.
        """
        raise NotImplementedError("Subclasses must implement normalize_position")
