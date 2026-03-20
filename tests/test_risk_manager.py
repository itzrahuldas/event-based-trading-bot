
import pytest
from unittest.mock import MagicMock
from src.risk_manager import RiskManager

class MockConfig:
    class Risk:
        max_trades_per_day = 5
        risk_per_trade = 0.01
        max_daily_loss = 1000.0
    risk = Risk()

@pytest.fixture
def risk_manager():
    broker = MagicMock()
    broker.get_cash.return_value = 100000.0
    
    rm = RiskManager(broker)
    rm.config = MockConfig() # Override config
    return rm

def test_daily_loss_limit(risk_manager):
    assert risk_manager.can_trade() is True
    
    # Simulate a small loss
    risk_manager.update_metrics(-500.0)
    assert risk_manager.can_trade() is True
    assert risk_manager.is_kill_switch_active is False
    
    # Simulate a detailed loss making total -1500 (limit 1000)
    risk_manager.update_metrics(-1000.0)
    assert risk_manager.is_kill_switch_active is True
    assert risk_manager.can_trade() is False

def test_max_drawdown_halt(risk_manager):
    # Initial Equity 100k
    risk_manager.broker.get_cash.return_value = 100000.0
    
    # Simulate a trade that updates metrics (and peak equity)
    # Peak becomes 100k
    risk_manager.update_metrics(0) 
    assert risk_manager.peak_equity == 100000.0
    
    # Simulate Massive Drawdown (Equity drops to 90k -> 10% drop, > 5% allowed)
    risk_manager.broker.get_cash.return_value = 90000.0
    risk_manager.update_metrics(0) # Logic checks current equity vs peak
    
    assert risk_manager.is_halted_drawdown is True
    assert risk_manager.can_trade() is False
