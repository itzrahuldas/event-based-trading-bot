import sys
import os
import time
import requests
from datetime import datetime
import pytz

# Add src to path
sys.path.append(os.getcwd())

from src.database import SessionLocal, Trade
from src.constants import Mode
from src.utils.time import now_utc

def main():
    print("🚀 Test Scenario Started. Waiting 30s for browser to be ready...")
    time.sleep(30)
    
    # 1. Insert into DB
    print("Writing Trade to DB...")
    db = SessionLocal()
    try:
        t = Trade(
            timestamp=now_utc(),
            ticker="TCS",
            side="BUY",
            quantity=10,
            price=3500.50,
            pnl=0.0,
            reason="TEST_SCENARIO",
            mode=Mode.PAPER, # Using PAPER so it shows in PAPER view
            strategy_version="TEST"
        )
        db.add(t)
        db.commit()
        print(f"Trade inserted: ID={t.id}")
    except Exception as e:
        print(f"DB Error: {e}")
        db.rollback()
    finally:
        db.close()
        
    # 2. Trigger Webhook
    print("Triggering Webhook...")
    try:
        data = {
            "type": "TRADE_ENTRY",
            "data": {
                "message": f"🚀 LIVE BUY: TCS @ 3500.50 (Simulated)"
            }
        }
        resp = requests.post("http://localhost:8000/webhook/notify", json=data)
        print(f"Webhook Status: {resp.status_code}")
    except Exception as e:
        print(f"Webhook Error: {e}")

if __name__ == "__main__":
    main()
