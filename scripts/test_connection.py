import sys
import os
import logging
from kiteconnect import KiteConnect

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.config import load_config

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ConnectionTester")

def test_zerodha_connection():
    print("\n--- Zerodha Connection Tester ---\n")
    
    # 1. Load Config
    try:
        config = load_config()
        z_conf = config.zerodha
        print(f"[1] Configuration Loaded.")
        print(f"    - API Key: {'*' * 4 + z_conf.api_key[-4:] if z_conf.api_key else 'MISSING'}")
        print(f"    - Access Token: {'*' * 4 + z_conf.access_token[-4:] if z_conf.access_token else 'MISSING'}")
    except Exception as e:
        print(f"[X] Failed to load config: {e}")
        return

    if not z_conf.api_key or not z_conf.access_token:
        print("\n[!] CRITICAL: API Key or Access Token is missing in .env")
        print("    Please fill in ZERODHA_API_KEY and ZERODHA_ACCESS_TOKEN.")
        return

    # 2. Initialize KiteConnect
    try:
        kite = KiteConnect(api_key=z_conf.api_key)
        kite.set_access_token(z_conf.access_token)
        print("[2] KiteConnect Initialized.")
    except Exception as e:
        print(f"[X] Failed to initialize KiteConnect: {e}")
        return

    # 3. Test Connectivity (Fetch Profile/Margins)
    print("[3] Verifying Session (Fetching Profile)...")
    try:
        # Fetch Profile
        profile = kite.profile()
        user_name = profile.get('user_name')
        uid = profile.get('user_id')
        print(f"    [SUCCESS] Logged in as: {user_name} ({uid})")
        
        # Fetch Margins
        print("[4] Checking Margins...")
        margins = kite.margins()
        equity_net = margins['equity']['net']
        print(f"    [SUCCESS] Equity Net Balance: ₹ {equity_net:,.2f}")
        
        print("\n[✓] CONNECTION SUCCESSFUL. SYSTEM IS READY FOR TRADING.")

    except Exception as e:
        print(f"\n[X] CONNECTION FAILED: {str(e)}")
        if "TokenException" in str(e) or "UserException" in str(e):
            print("\n    [!] Your Access Token is likely invalid or expired.")
            print("    [!] Please generate a new Access Token manually via the Login URL.")
            print(f"    [!] Login URL: {kite.login_url()}")
            
if __name__ == "__main__":
    test_zerodha_connection()
