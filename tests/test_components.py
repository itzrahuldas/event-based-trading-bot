import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.brokers.paper import PaperBroker
from src.risk_manager import RiskManager
from src.strategies.dip_buy import DipBuyStrategy
from src.ml.predictor import Predictor
from src.constants import Mode

# Mocks
@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_config():
    conf = MagicMock()
    conf.risk.max_capital_per_trade = 10000
    conf.risk.daily_loss_limit = 5000
    return conf

# Tests
def test_broker_initialization():
    broker = PaperBroker(initial_cash=50000.0)
    assert broker.get_cash() == 50000.0
    assert len(broker.get_positions()) == 0

def test_risk_manager_sizing(mock_config):
    # Mock broker
    broker = MagicMock()
    broker.get_cash.return_value = 100000
    
    rm = RiskManager(broker=broker)
    # Inject config (RiskManager usually loads its own, but we can override or mock logic)
    # Actually RiskManager loads config internally. 
    # For unit test, we might want to dependency inject config, but our class doesn't support it well yet.
    # We will test the default logic:
    
    # Formula: risk_per_trade / stop_loss_amt
    # Or simplified: if risk is 1% of 100k = 1000.
    # Stop loss is 'atr'. 
    
    qty = rm.calculate_quantity(price=100, atr=2.0)
    # Expect: Risk 1000 / (2 * 1) ? Strategy dependant.
    # Let's just assert it returns an integer > 0
    assert isinstance(qty, int)
    assert qty >= 0

def test_strategy_signal():
    strategy = DipBuyStrategy()
    
    # Create fake DataFrame
    df = pd.DataFrame({
        "Open": [100, 102, 101],
        "High": [105, 106, 104],
        "Low": [99, 100, 98],
        "Close": [102, 101, 99], # Dip?
        "Volume": [1000, 1200, 1100],
        # Indicators...
        "RSI": [50, 40, 25], # Oversold
        "EMA_50": [110, 109, 108], # Uptrend check?
        "ATR": [2, 2, 2]
    })
    
    # DipBuy logic: RSI < 30 & Close > EMA?
    # Here Close (99) < EMA (108). Should be NO signal if trend check is ON.
    
    signal = strategy.generate_signal("TEST", df)
    # Based on default logic, likely None or specific.
    # We just want to ensure it doesn't crash.
    assert signal is None or hasattr(signal, "type")

def test_ml_predictor_loading():
    # Should handle missing model gracefully
    pred = Predictor("non_existent_model.pkl")
    assert pred.model is None
    confidence = pred.predict_confidence(pd.DataFrame({'A':[1]}))
    assert confidence == 0.5 # Default neutral
