import sys
import os

sys.path.append(os.getcwd())

print("Attempting to import src.constants...")
try:
    from src.constants import Mode
    print("SUCCESS: src.constants")
except ImportError as e:
    print(f"FAILED: src.constants - {e}")

print("Attempting to import src.models.domain...")
try:
    from src.models.domain import OrderRequest
    print("SUCCESS: src.models.domain")
except ImportError as e:
    print(f"FAILED: src.models.domain - {e}")

print("Attempting to import src.risk_manager...")
try:
    from src.risk_manager import RiskManager
    print("SUCCESS: src.risk_manager")
except ImportError as e:
    print(f"FAILED: src.risk_manager - {e}")

print("Attempting to import src.execution.order_manager...")
try:
    from src.execution.order_manager import OrderManager
    print("SUCCESS: src.execution.order_manager")
except ImportError as e:
    print(f"FAILED: src.execution.order_manager - {e}")
except Exception as e:
    print(f"ERROR: src.execution.order_manager crahsed - {e}")
