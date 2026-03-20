import sys
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.getcwd())

print("Attempting early import of Signal...")
try:
    from src.models.domain import Signal
    print("SUCCESS: Signal imported early.")
except ImportError as e:
    print(f"FAILED: Signal import - {e}")


def test_imports():
    print("----------------------------------------------------------------")
    print("[Test 1] Verifying Imports...")
    try:
        from src.execution.order_manager import OrderManager
        print("  - Successfully imported OrderManager")
        from src.live_trader import LiveTrader
        print("  - Successfully imported LiveTrader")
        return True
    except ImportError as e:
        print(f"  [FAIL] IMPORT ERROR: {e}")
        return False
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False

def test_ghost_trade_fix():
    print("----------------------------------------------------------------")
    print("[Test 2] Verifying Ghost Trade Fix (Idempotency)...")
    try:
        from src.execution.order_manager import OrderManager
        from src.models.domain import Trade
        from src.constants import Mode
        from src.utils.time import now_utc

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

        # 3. Mock DB Response
        # We need to ensure logic finds a "recent" trade.
        # Logic: check_if_already_traded -> db.query().filter()...first()
        mock_query = mock_db.query.return_value
        # Use side_effect to return itself for chained filter calls
        mock_query.filter.return_value = mock_query 
        
        # The .first() call should return a Trade object
        mock_query.first.return_value = Trade(
            ticker="TATASTEEL",
            side="BUY", 
            quantity=10, 
            price=150.0, 
            pnl=0.0,
            strategy="MANUAL",
            mode=Mode.PAPER,
            run_id="test_run",
            timestamp=now_utc() - timedelta(days=2) # 2 days ago
        )

        # 4. Call Logic
        print("  - Checking DB for existing TATASTEEL trade...")
        exists = om._check_if_already_traded("TATASTEEL", days=7)

        # 5. Assert
        if exists:
            print("  - [PASS] Logic correctly identified previous trade.")
            return True
        else:
            print("  - [FAIL] Logic did not find the trade!")
            return False
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("STARTING SANITY CHECK...")
    p1 = test_imports()
    p2 = test_ghost_trade_fix()
    
    if p1 and p2:
        print("\n[SUCCESS] ALL CHECKS PASSED. SYSTEM IS READY.")
        sys.exit(0)
    else:
        print("\n[FAILURE] SOME CHECKS FAILED.")
        sys.exit(1)
