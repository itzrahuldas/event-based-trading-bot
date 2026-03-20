import sys
import os
import unittest
from unittest.mock import MagicMock
import pytest

# Ensure src is in path
sys.path.append(os.getcwd())

from src.brokers import PaperBroker
from src.risk_manager import RiskManager
from src.models.trading_domain import OrderRequest
from src.utils.config import load_config
from src.utils.logger import configure_logger

configure_logger()


class TestPhase2(unittest.TestCase):
    def setUp(self):
        self.broker = PaperBroker(initial_cash=100000.0)
        self.risk_manager = RiskManager(broker=self.broker)

        # Mock Config to deterministic values
        self.risk_manager.config.risk.risk_per_trade = 0.01
        self.risk_manager.config.risk.max_trades_per_day = 5
        self.risk_manager.config.risk.max_daily_loss = 5000.0

        # Mock Broker Config
        self.broker.config.backtest.slippage_bps = 0
        self.broker.config.backtest.brokerage = 10.0

    def test_position_sizing(self):
        # Case 1: Standard Trade
        # Cash = 100k, Risk = 1% = 1000
        # Price = 100, ATR = 5 => SL Price = 90 (Dist = 10)
        # Qty = 1000 / 2*ATR(10) = 100 shares

        qty = self.risk_manager.calculate_quantity(price=100.0, atr=5.0)
        self.assertEqual(qty, 100)

    @pytest.mark.skip(reason="RiskManager kill switch method not implemented yet")
    def test_kill_switch(self):
        self.assertFalse(self.risk_manager.is_kill_switch_active)

        # Simulate loss > max_loss (5000)
        self.risk_manager.update_daily_metrics(-6000.0)

        self.assertTrue(self.risk_manager.is_kill_switch_active)
        self.assertFalse(self.risk_manager.can_trade())

    def test_broker_order_execution(self):
        # Set LTP
        self.broker.update_ltp("TCS.NS", 100.0)

        order = OrderRequest(ticker="TCS.NS", side="BUY", quantity=10)
        fill = self.broker.place_order(order)

        self.assertIsNotNone(fill)
        self.assertEqual(fill.quantity, 10)
        self.assertEqual(self.broker.positions["TCS.NS"], 10)

        # Cash check: 100k - (10*100 + 10 brokerage) = 98990
        expected_cash = 100000.0 - 1000.0 - 10.0
        self.assertEqual(self.broker.get_cash(), expected_cash)

    def test_insufficient_funds(self):
        self.broker.cash = 50.0
        order = OrderRequest(ticker="TCS.NS", side="BUY", quantity=10, price=100.0)
        fill = self.broker.place_order(order)
        self.assertIsNone(fill)


if __name__ == "__main__":
    unittest.main()