import sys
import os
import re
try:
    from fyers_apiv3 import fyersModel
except ImportError as e:
    print(f"ERROR: fyers-apiv3 not installed or import failed. Details: {e}")
    print(f"Sys Path: {sys.path}")
    sys.exit(1)

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils.config import load_config
# We use load_dotenv manually to ensure we catch strings even if config.py defaults are empty
from dotenv import load_dotenv

ENV_PATH = os.path.join(os.path.dirname(__file__), '..', '.env')

def save_access_token_to_env(access_token):
    """
    Updates the .env file with the new Access Token.
    """
    print(f"\n[>] Saving Access Token to {ENV_PATH}...")
    
    with open(ENV_PATH, 'r') as f:
        content = f.read()
    
    # Regex to find FYERS_ACCESS_TOKEN=...
    # If exists, replace. If not, append.
    pattern = r"(FYERS_ACCESS_TOKEN=)(.*)"
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, f"\\1{access_token}", content)
    else:
        new_content = content + f"\nFYERS_ACCESS_TOKEN={access_token}\n"
        
    with open(ENV_PATH, 'w') as f:
        f.write(new_content)
    
    print("[✓] .env updated successfully.")

def authenticate():
    print("--- Fyers Auto-Authenticator ---\n")
    load_dotenv(ENV_PATH)
    
    client_id = os.getenv("FYERS_CLIENT_ID")
    secret_key = os.getenv("FYERS_SECRET_KEY")
    redirect_uri = os.getenv("FYERS_REDIRECT_URI", "http://127.0.0.1:3000")
    
    if not client_id or not secret_key:
        print("[!] Error: FYERS_CLIENT_ID or FYERS_SECRET_KEY missing in .env")
        return

    # 1. Generate Session & Auth URL
    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_uri,
        response_type="code",
        grant_type="authorization_code"
    )
    
    auth_link = session.generate_authcode()
    print("Step 1: Login via this URL:")
    print(f"\n{auth_link}\n")
    
    # 2. Input Auth Code
    print("Step 2: Copy the 'auth_code' from the Redirect URL.")
    auth_code = input("Paste Auth Code here: ").strip()
    
    if not auth_code:
        print("[!] No code entered. Aborting.")
        return
        
    # 3. Generate Token
    session.set_token(auth_code)
    try:
        response = session.generate_token()
        # Response: {'s': 'ok', 'code': 200, 'message': '...', 'access_token': '...'}
        
        if response.get('s') == 'ok':
            access_token = response.get('access_token')
            print(f"\n[Success] Access Token Generated: {access_token[:10]}...{access_token[-5:]}")
            save_access_token_to_env(access_token)
            print("\n[!] IMPORTANT: Restart your Trading Bot for changes to take effect.")
        else:
            print(f"\n[Failed] Could not generate token: {response}")
            
    except Exception as e:
        print(f"\n[Error] Exception during token generation: {e}")

if __name__ == "__main__":
    authenticate()
