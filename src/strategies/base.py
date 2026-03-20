from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd
from src.domain_models import Signal
from src.utils.logger import get_logger

logger = get_logger(__name__)

class Strategy(ABC):
    """
    Abstract Base Class for all Trading Strategies.
    """
    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version
        
    @abstractmethod
    def generate_signal(self, ticker: str, data: pd.DataFrame) -> Optional[Signal]:
        """
        Analyze data and return Signal object if any.
        """
        pass
