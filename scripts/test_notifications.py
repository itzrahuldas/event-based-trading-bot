import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.notify.notification_manager import NotificationManager, EventType
from src.utils.config import load_config
import time

def main():
    print("Testing Notification System...")
    
    # 1. Check Env
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ FAILED: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing in .env")
        sys.exit(1)
        
    print(f"✅ Found Credentials (Token: ...{token[-4:]})")
    
    # 2. Init Manager
    # We pass config just to trigger lazy loading if needed, but manager reads os.getenv
    config = load_config()
    manager = NotificationManager(config)
    
    if not manager.enabled:
        print("❌ Manager disabled despite credentials?")
        sys.exit(1)

    # 3. Send Test Message
    msg = "🚀 *Test Notification* from Event-Based Bot v4.0"
    print("Sending message...")
    manager.send(EventType.DAILY_SUMMARY, msg)
    
    # Wait for thread
    time.sleep(2)
    print("Check your Telegram!")

if __name__ == "__main__":
    main()
