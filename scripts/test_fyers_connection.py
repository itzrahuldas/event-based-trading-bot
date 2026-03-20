import sys
import os
import logging
try:
    from fyers_apiv3 import fyersModel
except ImportError:
    print("ERROR: fyers-apiv3 not installed. Run 'pip install fyers-apiv3'")
    sys.exit(1)

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.config import load_config

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_fyers_connection():
    print("\n--- Fyers Connection Tester ---\n")
    
    # 1. Load Config
    try:
        config = load_config()
        f_conf = config.fyers
        print(f"[1] Configuration Loaded.")
        print(f"    - Client ID: {f_conf.client_id}")
    except Exception as e:
        print(f"[X] Failed to load config: {e}")
        return

    if not f_conf.client_id or not f_conf.access_token:
        print("\n[!] CRITICAL: FYERS_CLIENT_ID or FYERS_ACCESS_TOKEN is missing.")
        print("    Please check your .env file.")
        
        # Helper for Token Generation URL
        if f_conf.client_id and f_conf.secret_key:
             session = fyersModel.SessionModel(
                 client_id=f_conf.client_id,
                 secret_key=f_conf.secret_key,
                 redirect_uri=f_conf.redirect_uri,
                 response_type="code",
                 grant_type="authorization_code"
             )
             print(f"\n    [TIP] Generate Access Token URL: {session.generate_authcode()}")
        return

    # 2. Initialize Model
    print("[2] Initializing FyersModel...")
    try:
        fyers = fyersModel.FyersModel(
            client_id=f_conf.client_id,
            token=f_conf.access_token,
            is_async=False,
            log_path=""
        )
    except Exception as e:
        print(f"[X] Init Failed: {e}")
        return

    # 3. Test Connectivity (Fetch Profile)
    print("[3] Verifying Session (Fetching Profile)...")
    try:
        response = fyers.get_profile()
        # Response: {'s': 'ok', 'data': {'name': '...', ...}}
        
        if response.get('s') == 'ok':
            data = response.get('data', {})
            name = data.get('name')
            fy_id = data.get('fy_id')
            print(f"    [SUCCESS] Logged in as: {name} ({fy_id})")
            print("\n[✓] CONNECTION SUCCESSFUL. SYSTEM IS READY FOR TRADING.")
        else:
             print(f"    [X] Profile Fetch Failed: {response}")
             if response.get('code') == -1: # Invalid Token
                  print("    [!] Access Token Invalid/Expired.")
    except Exception as e:
        print(f"\n[X] CONNECTION FAILED: {str(e)}")

if __name__ == "__main__":
    test_fyers_connection()
