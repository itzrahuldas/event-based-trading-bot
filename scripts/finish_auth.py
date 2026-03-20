import sys
import os
import re
from fyers_apiv3 import fyersModel
from dotenv import load_dotenv

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

ENV_PATH = os.path.join(os.path.dirname(__file__), '..', '.env')
AUTH_CODE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiIwWlpVWDRLOUFPIiwidXVpZCI6ImMxZDQ2ZGUyZGYwOTQ0MDFhNzg1YmEzNWQ1NTc3OGQ2IiwiaXBBZGRyIjoiIiwibm9uY2UiOiIiLCJzY29wZSI6IiIsImRpc3BsYXlfbmFtZSI6IkZBSDk5MjY3Iiwib21zIjoiSzEiLCJoc21fa2V5IjoiNGZkZDI5ODE3Mjk0ZjEzNDBjYjU2NjYzYzE3MTNlMmE0YmEzOGRmODgwMGZlNWFiMWViN2UyNDAiLCJpc0RkcGlFbmFibGVkIjoiTiIsImlzTXRmRW5hYmxlZCI6Ik4iLCJhdWQiOiJbXCJkOjFcIixcImQ6MlwiLFwieDowXCIsXCJ4OjFcIixcIng6MlwiXSIsImV4cCI6MTc2ODgzODA3MiwiaWF0IjoxNzY4ODA4MDcyLCJpc3MiOiJhcGkubG9naW4uZnllcnMuaW4iLCJuYmYiOjE3Njg4MDgwNzIsInN1YiI6ImF1dGhfY29kZSJ9.4IG-KGHij5ahLsZf-mRDBBWzkG3rsHOYHhGQUR5O9fA"

def save_access_token_to_env(access_token):
    print(f"\n[>] Saving Access Token to {ENV_PATH}...")
    with open(ENV_PATH, 'r') as f:
        content = f.read()

    pattern = r"(FYERS_ACCESS_TOKEN=)(.*)"
    if re.search(pattern, content):
        new_content = re.sub(pattern, f"\\1{access_token}", content)
    else:
        new_content = content + f"\nFYERS_ACCESS_TOKEN={access_token}\n"

    with open(ENV_PATH, 'w') as f:
        f.write(new_content)
    print("[✓] .env updated successfully.")

def finish_auth():
    print("--- Fyers Auth Finisher ---\n")
    load_dotenv(ENV_PATH)

    client_id = os.getenv("FYERS_CLIENT_ID")
    secret_key = os.getenv("FYERS_SECRET_KEY")
    redirect_uri = os.getenv("FYERS_REDIRECT_URI", "http://127.0.0.1:3000")

    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_uri,
        response_type="code",
        grant_type="authorization_code"
    )

    session.set_token(AUTH_CODE)
    try:
        response = session.generate_token()
        if response.get('s') == 'ok':
            access_token = response.get('access_token')
            save_access_token_to_env(access_token)
            print("LOGIN SUCCESSFUL")
        else:
            print(f"\n[Failed] Could not generate token: {response}")
    except Exception as e:
        print(f"\n[Error] Exception during token generation: {e}")

if __name__ == "__main__":
    finish_auth()
