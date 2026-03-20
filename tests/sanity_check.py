import sys
import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestSanity(unittest.TestCase):
    def test_01_imports(self):
        print("\n[Test 1] Verifying Imports...")
        try:
            from src.execution.order_manager import OrderManager
            print("  - Successfully imported OrderManager")
            from src.live_trader import LiveTrader
            print("  - Successfully imported LiveTrader")
        except ImportError as e:
            self.fail(f"IMPORT ERROR: {e}")
        except Exception as e:
            self.fail(f"UNKNOWN ERROR during import: {e}")

    def test_02_ghost_trade_fix(self):
        print("\n[Test 2] Verifying Ghost Trade Fix (Idempotency)...")
        from src.execution.order_manager import OrderManager
        from src.models.domain import Trade
        from src.constants import Mode

        # 1. Mock Dependencies
        mock_db = MagicMock()
        mock_broker = MagicMock()
        mock_risk = MagicMock()
        mock_run = MagicMock()
        mock_notify = MagicMock()

        # 2. Initialize OrderManager
        om = OrderManager(
            db=mock_db,
            broker=mock_broker,
            risk_manager=mock_risk,
            run_manager=mock_run,
            notifier=mock_notify,
            mode=Mode.PAPER
        )

        # 3. Mock DB Response ("Last trade was 2 days ago")
        # Structure: db.query(...).filter(...).filter(...).first() -> TradeObject
        # We need to ensure the chain returns a value.
        mock_query = mock_db.query.return_value
        mock_filter_1 = mock_query.filter.return_value
        # Since logic filters multiple times, we just need the final return to be the Trade object
        # Depending on how sqlalchemy chain is mocked, usually filter() returns the query object again.
        mock_filter_1.filter.return_value = mock_filter_1 # Chain filters
        mock_filter_1.first.return_value = Trade(
            ticker="TATASTEEL",
            side="BUY", 
            quantity=10, 
            price=150.0, 
            pnl=0.0,
            strategy="MANUAL",
            mode=Mode.PAPER,
            run_id="test_run",
            timestamp=datetime.utcnow()
        )

        # 4. Call Logic
        print("  - Checking DB for existing TATASTEEL trade...")
        # Accessing protected member for verification as requested
        exists = om._check_if_already_traded("TATASTEEL", days=7)

        # 5. Assert
        if exists:
            print("  - CHECK PASSED: Logic correctly identified previous trade.")
        else:
            print("  - CHECK FAILED: Logic did not find the trade.")
            
        self.assertTrue(exists, "Sanity Check Failed: Idempotency check returned False but should be True.")

if __name__ == '__main__':
    unittest.main()
