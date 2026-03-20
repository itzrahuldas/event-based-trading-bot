import sys
import os

sys.path.append(os.getcwd())

print("Attempting to import src.live_trader...")
try:
    from src.live_trader import LiveTrader
    print("SUCCESS: src.live_trader")
except ImportError as e:
    print(f"FAILED: src.live_trader - {e}")
except Exception as e:
    import traceback
    traceback.print_exc()
