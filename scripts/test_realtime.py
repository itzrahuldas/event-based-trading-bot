
import requests
import time

print("Waiting 10s before sending trigger...")
time.sleep(10)

print("Sending Test Webhook...")
try:
    resp = requests.post("http://localhost:8000/webhook/notify", json={
        "type": "TRADE_ENTRY",
        "data": {"message": "🚀 TEST TRADE: BUY TCS @ 3500"}
    })
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
except Exception as e:
    print(f"Error: {e}")
